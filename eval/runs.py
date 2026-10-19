"""Where eval runs are saved, and the comparison table over all of them.

Layout:
    eval/results/
        README.md                      # generated: one table per kind, newest run first
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
    """"dense", or "dense +exp" for a run with query expansion."""
    return config["mode"] + (" +exp" if config.get("expand") else "")


def _fusion(config: dict) -> str:
    """How lists were merged, e.g. "k=2; queries: max/10". "-" when nothing was fused.

    Runs from before these keys were recorded used RRF with k=60.
    """
    parts = []
    if config["mode"] == "hybrid":
        parts.append(f"k={config.get('rrf_k', 60)}")
    if config.get("expand"):
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


def answers_table(runs: list[dict], results_dir: Path) -> list[str]:
    lines = ["| run | index | mode | fusion | neighbours | k | answer model | judge | prompts | unjudged "
             "| correct | correct or partial | faithful | out-of-scope refused | false refusals | note |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for run in runs:
        c, s = run["config"], run["summary"]
        metrics = " | ".join(fmt(s[m]) if s[m]["n"] else "-" for m in ("correct", "correct_or_partial", "faithful",
                                                  "refusal_out_of_scope", "false_refusal_in_scope"))
        lines.append(f"| {_link(run, results_dir)} | {c['index']} | {_mode(c)} | {_fusion(c)} | {_nb(c)} | {c['k']} "
                     f"| {c['answer_model']} | {c['judge_model']} | {c['prompts_sha']} "
                     f"| {s['unjudged']}/{c['n_answered']} | {metrics} | {c.get('note', '')} |")
    return lines


def write_index(results_dir: Path = RESULTS_DIR) -> Path:
    lines = [
        "# Eval results", "",
        "Generated by `eval/runs.py`; do not edit by hand. Rebuild with `uv run python eval/compare.py`.",
        "Each run folder has `config.json` (full config), `summary.json`, `rows.json` and `report.md`.",
        "Run id = `<date>_<config hash>`. Compare two configs: `uv run python eval/compare.py diff <id> <id>`.",
        "",
        "Rates are shown with raw counts, e.g. `0.82 (18/22)`: with ~22 questions one question is ~5 points.",
        "",
        "## Retrieval", "",
        "**strict** = an expected section makes up at least 30% of the chunk; **section** = the chunk "
        "touches an expected section; **phrase** = the chunk contains an expected phrase.", "",
        *retrieval_table(load_runs("retrieval", results_dir), results_dir), "",
        "## Answers (LLM judge)", "",
        "Correct and false refusals are over judged in-scope questions; faithful over all judged ones. "
        "`prompts` is a hash of the answer + judge prompts.", "",
        *answers_table(load_runs("answers", results_dir), results_dir), "",
    ]
    path = results_dir / "README.md"
    path.write_text("\n".join(lines))
    return path
