"""Where eval runs are saved, and the comparison table over all of them.

Layout:
    eval/results/
        README.md                      # generated: the key runs listed in key_runs.json
        all_runs.md                    # generated: every run, one table per kind, newest first
        key_runs.json                  # hand-kept: which runs README.md shows, with a label each
        retrieval/<run_id>/            # kind = "retrieval" or "answers"
            config.json                # everything needed to reproduce the run
            summary.json               # the metrics
            rows.json                  # per-question details
            report.md                  # human-readable report

run_id = <date>_<config hash>, e.g. 2026-10-18_3f2a9c1b. The hash covers the settings that
change results (index, mode, models, prompts, questions...), not bookkeeping like the git
commit. So re-running the same config on the same day replaces that run (useful when a
judge run stopped halfway on quota), while any config change gets a new folder. Older
versions of a run are still in git history.
"""

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

from judge import fmt
from metrics import format_metric

RESULTS_DIR = Path(__file__).parent / "results"
KINDS = ("retrieval", "answers")

# Bookkeeping: recorded in config.json but left out of the hash.
UNHASHED = {"run_id", "kind", "created", "config_hash", "note", "git_commit", "n_answered"}
# Index manifest fields that describe the build, not the index's content.
UNHASHED_MANIFEST = {"created", "stats"}


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:8]


def config_hash(config: dict) -> str:
    stable = {k: v for k, v in config.items() if k not in UNHASHED}
    if "index_manifest" in stable:
        stable["index_manifest"] = {k: v for k, v in stable["index_manifest"].items()
                                    if k not in UNHASHED_MANIFEST}
    return hashlib.sha256(json.dumps(stable, sort_keys=True).encode()).hexdigest()[:8]


def stamp(kind: str, config: dict, note: str = "", created: datetime | None = None) -> dict:
    """Return the config with run_id, kind, created, config_hash (and note) added at the top."""
    created = created or datetime.now()
    h = config_hash(config)
    meta = {"run_id": f"{created.date().isoformat()}_{h}", "kind": kind,
            "created": created.isoformat(timespec="seconds"), "config_hash": h, "note": note}
    return meta | config


def save_run(config: dict, summary: dict, rows: list[dict], report: str,
             results_dir: Path = RESULTS_DIR) -> Path:
    """Write one run's files (replacing a same-day run of the same config), then the index."""
    run_dir = results_dir / config["kind"] / config["run_id"]
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    for name, data in (("config", config), ("summary", summary), ("rows", rows)):
        (run_dir / f"{name}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    (run_dir / "report.md").write_text(report)
    write_index(results_dir)
    return run_dir


def load_runs(kind: str, results_dir: Path = RESULTS_DIR) -> list[dict]:
    """[{"config", "summary", "dir"}] for every run of this kind, newest first."""
    runs = []
    for config_file in (results_dir / kind).glob("*/config.json"):
        run_dir = config_file.parent
        runs.append({"config": json.loads(config_file.read_text()),
                     "summary": json.loads((run_dir / "summary.json").read_text()),
                     "dir": run_dir})
    return sorted(runs, key=lambda r: r["config"]["created"], reverse=True)


def find_run(run_id: str, results_dir: Path = RESULTS_DIR) -> dict:
    """Look a run up by its id, or by any unique prefix of the id or the config hash."""
    matches = [r for kind in KINDS for r in load_runs(kind, results_dir)
               if r["config"]["run_id"].startswith(run_id) or r["config"]["config_hash"].startswith(run_id)]
    if len(matches) != 1:
        raise SystemExit(f"{run_id!r} matches {len(matches)} runs; give more of the id.")
    return matches[0]


def flatten(d: dict, prefix: str = "") -> dict:
    """{"a": {"b": 1}} -> {"a.b": 1}, so nested configs can be compared key by key."""
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out |= flatten(v, f"{prefix}{k}.")
        else:
            out[f"{prefix}{k}"] = v
    return out


def config_diff(a: dict, b: dict) -> list[tuple[str, object, object]]:
    """[(key, value in a, value in b)] for every config key that differs."""
    fa, fb = flatten(a), flatten(b)
    return [(k, fa.get(k), fb.get(k)) for k in sorted(fa.keys() | fb.keys()) if fa.get(k) != fb.get(k)]


# --- The comparison table (eval/results/README.md) ---

def _nb(config: dict) -> str:
    return "yes" if config.get("neighbours") else "no"


def _mode(config: dict) -> str:
    """"dense", or "dense +exp +rr" for a run with query expansion and a reranker."""
    return config["mode"] + (" +exp" if config.get("expand") else "") + (" +rr" if config.get("rerank") else "")


def _fusion(config: dict) -> str:
    """How lists were merged, e.g. "k=2; queries: max/10". "-" when nothing was fused.

    Runs from before these keys were recorded used RRF with k=60.
    """
    parts = []
    if config["mode"] == "hybrid":
        parts.append(f"k={config.get('rrf_k', 60)}")
    if config.get("rerank"):  # the reranker replaces the queries' fusion
        parts.append(f"rerank: {config['rerank_model'].split('/')[-1]}/{config['rerank_candidates']}")
    elif config.get("expand"):
        parts.append(f"queries: {config.get('expand_fusion', 'rrf')}/{config.get('expand_candidates', '?')}")
    return "; ".join(parts) or "-"


def _link(run: dict, results_dir: Path) -> str:
    c = run["config"]
    return f"[{c['run_id']}]({(run['dir'] / 'report.md').relative_to(results_dir).as_posix()})"


def retrieval_table(runs: list[dict], results_dir: Path) -> list[str]:
    lines = ["| run | index | mode | fusion | neighbours | n | strict hit@1 | strict hit@3 | strict hit@5 "
             "| strict MRR | section hit@5 | phrase hit@5 | note |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for run in runs:
        c, s = run["config"], run["summary"]["all"]
        strict = " | ".join(format_metric(s["strict"], m) for m in ("hit@1", "hit@3", "hit@5", "mrr"))
        lines.append(f"| {_link(run, results_dir)} | {c['index']} | {_mode(c)} | {_fusion(c)} | {_nb(c)} | {s['n']} "
                     f"| {strict} | {format_metric(s['section'], 'hit@5')} "
                     f"| {format_metric(s['phrase'], 'hit@5')} | {c.get('note', '')} |")
    return lines


def _answer_metrics(summary: dict, names: tuple[str, ...]) -> str:
    # "old_law" exists only for runs on trap questions (traps.jsonl).
    return " | ".join(fmt(summary[m]) if m in summary and summary[m]["n"] else "-" for m in names)


def answers_table(runs: list[dict], results_dir: Path) -> list[str]:
    lines = ["| run | index | mode | fusion | neighbours | k | answer model | judge | prompts | unjudged "
             "| correct | correct or partial | faithful | out-of-scope refused | false refusals | old law | note |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for run in runs:
        c, s = run["config"], run["summary"]
        metrics = _answer_metrics(s, ("correct", "correct_or_partial", "faithful", "refusal_out_of_scope",
                                      "false_refusal_in_scope", "old_law"))
        lines.append(f"| {_link(run, results_dir)} | {c['index']} | {_mode(c)} | {_fusion(c)} | {_nb(c)} | {c['k']} "
                     f"| {c['answer_model']} | {c['judge_model']} | {c['prompts_sha']} "
                     f"| {s['unjudged']}/{c['n_answered']} | {metrics} | {c.get('note', '')} |")
    return lines


def _short_metrics(run: dict | None) -> list[str]:
    """Strict hit@1, hit@5 as raw counts ("18/23") and MRR; "-" for each when there is no run."""
    if run is None:
        return ["-"] * 3
    s = run["summary"]["all"]["strict"]
    return [f"{s['hits@1']}/{s['n']}", f"{s['hits@5']}/{s['n']}", f"{s['mrr']:.2f}"]


# What the setup columns of the key runs tables mean (README.md).
SETUP_NOTES = [
    "- **search**: dense = embedding similarity; hybrid = dense + BM25 keyword search, merged with RRF.",
    "- **query expansion**: Gemini writes 3 extra search queries in the Act's wording; the question is searched "
    "too. Without a reranker, their result lists are merged (RRF in the earliest runs, best rank later).",
    "- **reranker**: a cross-encoder reads the question next to each pooled chunk and orders them. "
    "*question + half of best rewrite* = its score against the question plus half its best score against a rewrite.",
    "- **neighbours**: the chunks before and after each hit, if in the same section. On structured chunks that is "
    "always so, so they can't change these metrics; they give the answer model the rest of a sub-section or table.",
]


def _setup(config: dict) -> list[str]:
    """Search, query expansion, reranker and neighbours columns for one run."""
    reranker = "–"
    if config.get("rerank"):
        # Runs from before rerank_rewrite_weight existed scored against the question only.
        w = config.get("rerank_rewrite_weight", 0)
        reranker = f"question + {'half' if w == 0.5 else w} of best rewrite" if w else "question"
    return [config["mode"], "✓" if config.get("expand") else "–", reranker, "✓" if config.get("neighbours") else "–"]


def key_retrieval_table(keys: list[dict], runs: dict[str, dict], results_dir: Path) -> list[str]:
    """One row per step: what was switched on, then its dev and (optional) held-out run side by side.

    Steps look like {"id": "B1", "step": "...", "dev": "<run id>", "heldout": "<run id>"}; "id" is
    optional. The setup columns come from the dev run's config, else the held-out run's.
    """
    numbered = any("id" in key for key in keys)
    header = ["#"] * numbered + ["step", "search", "query expansion", "reranker", "neighbours", "dev hit@1",
                                 "dev hit@5", "dev MRR", "held-out hit@1", "held-out hit@5", "held-out MRR", "runs"]
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for key in keys:
        links, cells, configs = [], [], []
        for split, label in (("dev", "dev"), ("heldout", "held-out")):
            run_id = key.get(split)
            run = runs.get(run_id) if run_id else None
            cells += _short_metrics(run)
            if run is not None:
                links.append(f"[{label}](retrieval/{run_id}/report.md)")
                configs.append(run["config"])
            elif run_id:  # listed in key_runs.json but deleted or mistyped
                links.append(f"{run_id} (not found)")
        setup = _setup(configs[0]) if configs else ["-"] * 4
        row = [key.get("id", "")] * numbered + [key["step"], *setup, *cells, " · ".join(links)]
        lines.append("| " + " | ".join(row) + " |")
    return lines


def key_retrieval_groups(groups: list[dict], runs: dict[str, dict], results_dir: Path) -> list[str]:
    """Each group in key_runs.json: an optional "### heading" and note, then its table of steps."""
    lines = []
    for group in groups:
        if group.get("heading"):
            lines += [f"### {group['heading']}", ""]
        if group.get("note"):
            lines += [group["note"], ""]
        lines += [*key_retrieval_table(group["steps"], runs, results_dir), ""]
    return lines


def key_answers_table(keys: list[dict], runs: dict[str, dict], results_dir: Path) -> list[str]:
    lines = ["| step | judged | correct | correct or partial | faithful | false refusals | old law | run |",
             "|---|---|---|---|---|---|---|---|"]
    for key in keys:
        run = runs.get(key["run"])
        if run is None:
            lines.append(f"| {key['step']} | - | - | - | - | - | - | {key['run']} (not found) |")
            continue
        c, s = run["config"], run["summary"]
        metrics = _answer_metrics(s, ("correct", "correct_or_partial", "faithful", "false_refusal_in_scope",
                                      "old_law"))
        judged = c["n_answered"] - s["unjudged"]
        lines.append(f"| {key['step']} | {judged}/{c['n_answered']} | {metrics} | {_link(run, results_dir)} |")
    return lines


def write_index(results_dir: Path = RESULTS_DIR) -> Path:
    """Write README.md (the key runs from key_runs.json) and all_runs.md (every run)."""
    retrieval, answers = load_runs("retrieval", results_dir), load_runs("answers", results_dir)
    how_to = [
        "Generated by `eval/runs.py`; do not edit by hand. Rebuild with `uv run python eval/compare.py`.",
        "Each run folder has `config.json` (full config), `summary.json`, `rows.json` and `report.md`.",
        "Run id = `<date>_<config hash>`. Compare two configs: `uv run python eval/compare.py diff <id> <id>`.",
        "",
        "Rates are shown with raw counts, e.g. `0.92 (24/26)`: with this few questions, one question moves a rate "
        "by several points.",
    ]
    strict_note = ("**strict** = an expected section makes up at least 30% of the chunk; **section** = the chunk "
                   "touches an expected section; **phrase** = the chunk contains an expected phrase.")

    all_lines = [
        "# All eval runs", "", *how_to, "",
        "## Retrieval", "", strict_note, "",
        *retrieval_table(retrieval, results_dir), "",
        "## Answers (LLM judge)", "",
        "Correct and false refusals are over judged in-scope questions; faithful over all judged ones. "
        "`prompts` is a hash of the answer + judge prompts.", "",
        *answers_table(answers, results_dir), "",
    ]
    (results_dir / "all_runs.md").write_text("\n".join(all_lines))

    key_file = results_dir / "key_runs.json"
    keys = json.loads(key_file.read_text()) if key_file.exists() else {}
    by_id = {r["config"]["run_id"]: r for r in retrieval + answers}
    lines = [
        "# Eval results", "",
        "The steps that shaped the app. **hit@1** = the right section is the first result; "
        "**hit@5** = it is in the top 5; **MRR** = the mean of 1/rank of the first right result (1.00 = always "
        "first). A hit is *strict*: the section makes up at least 30% of the chunk. "
        "Dev = questions.jsonl, held-out = heldout.jsonl (written later, not used for tuning). "
        "Counts are questions: with this few, one question moves a rate by several points.", "",
        f"Generated from `key_runs.json` by `eval/runs.py` (`uv run python eval/compare.py`). "
        f"Every run ({len(retrieval)} retrieval, {len(answers)} answer) is in [all_runs.md](all_runs.md).", "",
        "## Retrieval: how the app was built", "",
        *SETUP_NOTES, "",
        *key_retrieval_groups(keys.get("retrieval", []), by_id, results_dir),
        "## Retrieval: also tried", "",
        *key_retrieval_groups(keys.get("also_tried", []), by_id, results_dir),
        "## Answers (LLM judge)", "",
        "Correct and false refusals are over judged in-scope questions; faithful over all judged ones. "
        "**Old law** (trap questions only, `traps.jsonl`) = answers that state a figure only the repealed "
        "text has; a regex check, no judge.", "",
        *key_answers_table(keys.get("answers", []), by_id, results_dir), "",
    ]
    path = results_dir / "README.md"
    path.write_text("\n".join(lines))
    return path
