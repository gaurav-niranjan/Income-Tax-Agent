"""Run the retrieval eval and save results.

Run: uv run python eval/run_eval.py --index fixed-1000-150__bge-base --modes dense bm25 hybrid

Each mode writes eval/results/<index>__<mode>__<date>.md and .json, with the full config.
Out-of-scope questions are skipped here: retrieval always returns *something*, so they
are only meaningful for the answer eval (--judge, Phase 7).
"""

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

from metrics import (
    KS,
    RULES,
    STRICT_SHARE,
    first_hit_ranks,
    format_metric,
    load_questions,
    summarize_by_type,
)

from income_tax_agent.config import get_settings
from income_tax_agent.retrieval.retriever import MODES, Retriever

EVAL_DIR = Path(__file__).parent
DEPTH = 10  # chunks retrieved per question; MRR is computed over these


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def run_mode(retriever: Retriever, questions, mode: str) -> list[dict]:
    rows = []
    for q in questions:
        hits = retriever.retrieve(q.question, mode=mode, k=DEPTH)
        chunks = [h.chunk for h in hits]
        rows.append(
            {
                "id": q.id,
                "type": q.type,
                "question": q.question,
                "expected_sections": q.sections,
                "ranks": first_hit_ranks(chunks, q),
                "retrieved": [{"chunk_id": c.chunk_id, "sections": c.sections} for c in chunks],
            }
        )
    return rows


def to_markdown(name: str, config: dict, summary: dict, rows: list[dict]) -> str:
    lines = [f"# Retrieval eval: {name}", "", "```json", json.dumps(config, indent=2), "```", ""]
    metric_names = [f"hit@{k}" for k in KS] + ["mrr"]
    for rule in RULES:
        lines += [f"## {rule}-hit", "", "| type | " + " | ".join(metric_names) + " |",
                  "|---|" + "---|" * len(metric_names)]
        for group, s in summary.items():
            cells = " | ".join(format_metric(s[rule], m) for m in metric_names)
            lines.append(f"| {group} | {cells} |")
        lines.append("")
    lines += ["## Per question (first-hit rank; - = none in top 10)", "",
              "| id | type | section | strict | phrase | expected | top-3 retrieved sections |",
              "|---|---|---|---|---|---|---|"]
    for r in rows:
        ranks = " | ".join(str(r["ranks"][rule] or "-") for rule in RULES)
        top3 = "; ".join(",".join(x["sections"]) for x in r["retrieved"][:3])
        lines.append(f"| {r['id']} | {r['type']} | {ranks} | {','.join(r['expected_sections'])} | {top3} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    settings = get_settings()
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default=settings.index_name)
    parser.add_argument("--modes", nargs="+", default=list(MODES), choices=MODES)
    parser.add_argument("--questions", type=Path, default=EVAL_DIR / "questions.jsonl")
    parser.add_argument("--limit", type=int, help="only the first N questions (quick runs)")
    parser.add_argument("--judge", action="store_true", help="answer eval with an LLM judge (Phase 7)")
    args = parser.parse_args()
    if args.judge:
        sys.exit("--judge is not implemented yet (Phase 7).")

    questions = [q for q in load_questions(args.questions)[: args.limit] if q.in_scope]
    retriever = Retriever(args.index, settings=settings)
    out_dir = EVAL_DIR / "results"
    out_dir.mkdir(exist_ok=True)

    print(f"{len(questions)} in-scope questions, index {args.index}")
    metric_names = [f"hit@{k}" for k in KS] + ["mrr"]
    for mode in args.modes:
        rows = run_mode(retriever, questions, mode)
        summary = summarize_by_type(rows)
        name = f"{args.index}__{mode}__{date.today().isoformat()}"
        config = {
            "index": args.index,
            "mode": mode,
            "depth": DEPTH,
            "strict_share": STRICT_SHARE,
            "rrf_k": settings.rrf_k,
            "hybrid_candidates": settings.hybrid_candidates,
            "query_prefix": settings.embedding_query_prefix,
            "questions_file": args.questions.name,
            "n_questions": len(questions),
            "git_commit": git_commit(),
            "index_manifest": retriever.manifest,
        }
        (out_dir / f"{name}.json").write_text(
            json.dumps({"config": config, "summary": summary, "rows": rows}, indent=2) + "\n"
        )
        (out_dir / f"{name}.md").write_text(to_markdown(name, config, summary, rows))
        s = summary["all"]
        for rule in RULES:
            cells = "  ".join(f"{m} {format_metric(s[rule], m):<13}" for m in metric_names)
            print(f"{mode:<7} {rule:<8} {cells}")
    print(f"Results in {out_dir}")


if __name__ == "__main__":
    main()
