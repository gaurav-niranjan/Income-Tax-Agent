"""Run the retrieval eval and save results.

Run: uv run python eval/run_eval.py --index fixed-1000-150__bge-base --modes dense bm25 hybrid
     add --neighbours to score each hit plus its same-section neighbours (what the LLM sees)

     add --note "why this run" to label it in the results table
     add --expand to search with LLM-written queries too (GEMINI_EXPAND_MODEL; cached on disk)

Each mode is one run, saved to eval/results/retrieval/<date>_<config hash>/ (see runs.py),
and eval/results/README.md is rebuilt to compare all runs.
Out-of-scope questions are skipped in the retrieval eval: retrieval always returns
*something*, so they only make sense for the answer eval.

Answer eval (Phase 7):
     uv run python eval/run_eval.py --judge [--limit 3] [--sleep 6]
Runs the full pipeline with the app's settings on all questions, then a second Gemini
model (GEMINI_JUDGE_MODEL) grades correctness, faithfulness and refusals. Saved to
eval/results/answers/<date>_<config hash>/. LLM calls are cached on disk.
"""

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path

from judge import JUDGE_SYSTEM, JUDGE_TEMPLATE, fmt, judge_prompt, parse_verdict, summarize_answers
from metrics import (
    KS,
    RULES,
    STRICT_SHARE,
    first_hit_ranks,
    format_metric,
    load_questions,
    summarize_by_type,
)
from runs import RESULTS_DIR, file_sha, save_run, stamp

from income_tax_agent.config import get_settings
from income_tax_agent.graph.build import build_graph
from income_tax_agent.llm import GeminiLLM, QuotaExhausted
from income_tax_agent.prompts import ANSWER_SYSTEM, EXPAND_SYSTEM, format_context
from income_tax_agent.retrieval.expand import expand_query
from income_tax_agent.retrieval.retriever import MODES, Retriever

EVAL_DIR = Path(__file__).parent
DEPTH = 10  # chunks retrieved per question; MRR is computed over these


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def expand_llm(settings) -> GeminiLLM:
    return GeminiLLM(settings.gemini_expand_model or settings.gemini_model, settings.google_api_key,
                     settings.llm_cache_dir, settings.gemini_temperature)


def expand_config(settings, llm: GeminiLLM) -> dict:
    """Added to a run's config only when expansion is on, so earlier runs keep their hashes."""
    return {"expand": True, "expand_model": llm.model_name,
            "expand_prompt_sha": hashlib.sha256(EXPAND_SYSTEM.encode()).hexdigest()[:8],
            "expand_candidates": settings.expand_candidates, "expand_fusion": settings.expand_fusion}


def label(mode: str, expand: bool, neighbours: bool) -> str:
    return mode + ("+exp" if expand else "") + ("+nb" if neighbours else "")


def expand_all(questions, llm: GeminiLLM, sleep: float) -> dict[str, list[str]]:
    """Expand every question once (reused by all modes). Stops early if the day's quota is gone."""
    queries = {}
    for q in questions:
        calls_before = llm.api_calls
        try:
            queries[q.id] = expand_query(q.question, llm)
        except QuotaExhausted as e:
            print(f"Stopping before {q.id}: {e}. Re-run later; finished calls are cached.")
            break
        if llm.api_calls > calls_before:
            time.sleep(sleep)  # free-tier rate limits; cached questions skip this
    print(f"Expanded {len(queries)} questions ({llm.api_calls} API calls, model {llm.model_name})")
    return queries


def run_mode(retriever: Retriever, questions, mode: str, neighbours: bool = False,
             queries: dict[str, list[str]] | None = None) -> list[dict]:
    rows = []
    for q in questions:
        searched = queries[q.id] if queries else [q.question]
        hits = retriever.retrieve_multi(searched, mode=mode, k=DEPTH)
        if neighbours:
            hits = retriever.expand_neighbours(hits)
        rows.append(
            {
                "id": q.id,
                "type": q.type,
                "question": q.question,
                "expected_sections": q.sections,
                "ranks": first_hit_ranks([(h.rank, h.chunk) for h in hits], q),
                "retrieved": [
                    {"chunk_id": h.chunk.chunk_id, "rank": h.rank, "sections": h.chunk.sections,
                     "neighbour_of": h.neighbour_of}
                    for h in hits
                ],
            }
            | ({"queries": searched} if queries else {})
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
    if any("queries" in r for r in rows):
        lines += ["", "## Expanded queries (the question itself is always searched too)", ""]
        for r in rows:
            lines += [f"**{r['id']}** {r['question']}", *(f"- {q}" for q in r["queries"][1:]), ""]
    return "\n".join(lines) + "\n"


def run_answer_eval(args, settings, retriever: Retriever, mode: str) -> None:
    """Phase 7: answer every question (out-of-scope included) and have a second model grade it."""
    answer_llm = GeminiLLM(settings.gemini_model, settings.google_api_key, settings.llm_cache_dir,
                           settings.gemini_temperature)
    judge_llm = GeminiLLM(args.judge_model or settings.gemini_judge_model, settings.google_api_key,
                          settings.llm_cache_dir)
    if judge_llm.model_name == answer_llm.model_name:
        print("WARNING: the judge is the same model as the answerer; grades may be biased.")
    exp_llm = expand_llm(settings)
    graph = build_graph(retriever, answer_llm, exp_llm)
    questions = load_questions(args.questions)[: args.limit]

    rows = []
    judge_quota_error = None  # once the judge's daily quota is gone, stop calling it
    for q in questions:
        calls_before = answer_llm.api_calls + judge_llm.api_calls + exp_llm.api_calls
        try:
            state = graph.invoke({"question": q.question, "mode": mode, "k": settings.answer_k,
                                  "neighbours": args.neighbours, "expand": args.expand})
        except QuotaExhausted as e:
            print(f"Stopping before {q.id}: {e}. Re-run later; finished calls are cached.")
            break
        context = format_context(state["hits"])
        verdict, error = None, judge_quota_error
        if judge_quota_error is None:
            try:
                reply = judge_llm.complete(JUDGE_SYSTEM, judge_prompt(q.question, q.reference, q.in_scope,
                                                                      context, state["answer"]))
                verdict = parse_verdict(reply)
            except QuotaExhausted as e:
                judge_quota_error = error = str(e)
                print(f"{e}. Answering the rest without grading; re-run later to grade them.")
            except ValueError as e:
                error = str(e)
        rows.append({
            "id": q.id, "type": q.type, "in_scope": q.in_scope, "question": q.question,
            "reference": q.reference, "answer": state["answer"],
            "retrieved": [{"chunk_id": h.chunk.chunk_id, "rank": h.rank, "sections": h.chunk.sections,
                           "neighbour_of": h.neighbour_of} for h in state["hits"]],
            "citations": state["citations"], "unsupported_citations": state["unsupported_citations"],
            "verdict": verdict, "judge_error": error,
        } | ({"queries": state["queries"], "expand_error": state.get("expand_error")} if args.expand else {}))
        v = verdict or {}
        print(f"{q.id} {q.type:<12} {v.get('correctness', 'UNJUDGED'):<9} "
              f"faithful={v.get('faithful')} refused={v.get('refused')}")
        if answer_llm.api_calls + judge_llm.api_calls + exp_llm.api_calls > calls_before:
            time.sleep(args.sleep)  # free-tier rate limits; cached questions skip this

    summary = summarize_answers(rows)
    name = label(mode, args.expand, args.neighbours)
    # The prompts are part of the config hash: a re-run with a changed prompt gets its own run.
    prompts_sha = hashlib.sha256((ANSWER_SYSTEM + JUDGE_SYSTEM + JUDGE_TEMPLATE).encode()).hexdigest()[:8]
    config = stamp("answers", {
        "index": args.index, "mode": mode, "neighbours": args.neighbours, "k": settings.answer_k,
        "rrf_k": settings.rrf_k, "hybrid_candidates": settings.hybrid_candidates,
        "answer_model": answer_llm.model_name, "judge_model": judge_llm.model_name,
        "prompts_sha": prompts_sha,  # identifies the prompt versions
        "questions_file": args.questions.name, "questions_sha": file_sha(args.questions),
        "n_questions": len(questions), "n_answered": len(rows),
        "git_commit": git_commit(), "index_manifest": retriever.manifest,
    } | (expand_config(settings, exp_llm) if args.expand else {}), note=args.note)
    run_dir = save_run(config, summary, rows, answers_markdown(config["run_id"], config, summary, rows))
    print(f"\nRun {config['run_id']} saved to {run_dir}")
    print(f"{name}: correct {fmt(summary['correct'])}, correct or partial {fmt(summary['correct_or_partial'])}, "
          f"faithful {fmt(summary['faithful'])}, out-of-scope refused {fmt(summary['refusal_out_of_scope'])}, "
          f"in-scope wrongly refused {fmt(summary['false_refusal_in_scope'])}, unjudged {summary['unjudged']}")
    print(f"API calls: answer model {answer_llm.api_calls}, judge {judge_llm.api_calls}, "
          f"expansion {exp_llm.api_calls}")


def answers_markdown(name: str, config: dict, summary: dict, rows: list[dict]) -> str:
    lines = [f"# Answer eval: {name}", "", "```json", json.dumps(config, indent=2), "```", "",
             "| metric | value |", "|---|---|",
             f"| correct (in scope) | {fmt(summary['correct'])} |",
             f"| correct or partial (in scope) | {fmt(summary['correct_or_partial'])} |",
             f"| faithful (all) | {fmt(summary['faithful'])} |",
             f"| refused, out of scope | {fmt(summary['refusal_out_of_scope'])} |",
             f"| refused, in scope (false refusals) | {fmt(summary['false_refusal_in_scope'])} |",
             f"| unjudged | {summary['unjudged']} |", "",
             "| type | correct | partial | incorrect |", "|---|---|---|---|"]
    for t, s in summary["by_type"].items():
        lines.append(f"| {t} | {fmt(s['correct'])} | {fmt(s['partial'])} | {fmt(s['incorrect'])} |")
    lines += ["", "## Every answer", ""]
    for r in rows:
        v = r["verdict"] or {}
        lines += [f"### {r['id']} ({r['type']}): {v.get('correctness', 'UNJUDGED')}, "
                  f"faithful={v.get('faithful')}, refused={v.get('refused')}",
                  f"**Q:** {r['question']}", "", f"**Reference:** {r['reference']}", "",
                  "**Answer:**", "", r["answer"], "",
                  *([f"**Also searched for:** {' | '.join(r['queries'][1:]) or '(nothing added)'}", ""]
                    if "queries" in r else []),
                  f"**Retrieved sections:** {'; '.join(','.join(x['sections']) for x in r['retrieved'])}", "",
                  f"**Judge:** {v.get('explanation') or r['judge_error']}"]
        if v.get("unsupported_claims"):
            lines.append(f"**Unsupported claims:** {v['unsupported_claims']}")
        lines.append("")
    return "\n".join(lines) + "\n"


def run_retrieval_eval(args, settings, retriever: Retriever) -> None:
    questions = [q for q in load_questions(args.questions)[: args.limit] if q.in_scope]
    print(f"{len(questions)} in-scope questions, index {args.index}")
    metric_names = [f"hit@{k}" for k in KS] + ["mrr"]
    queries, extra = None, {}
    if args.expand:
        llm = expand_llm(settings)
        queries = expand_all(questions, llm, args.sleep)
        questions = [q for q in questions if q.id in queries]
        extra = expand_config(settings, llm)
    for mode in args.modes:
        rows = run_mode(retriever, questions, mode, args.neighbours, queries)
        summary = summarize_by_type(rows)
        name = label(mode, args.expand, args.neighbours)
        config = stamp("retrieval", {
            "index": args.index,
            "mode": mode,
            "neighbours": args.neighbours,
            "depth": DEPTH,
            "strict_share": STRICT_SHARE,
            "rrf_k": settings.rrf_k,
            "hybrid_candidates": settings.hybrid_candidates,
            "query_prefix": settings.embedding_query_prefix,
            "questions_file": args.questions.name,
            "questions_sha": file_sha(args.questions),
            "n_questions": len(questions),
            "git_commit": git_commit(),
            "index_manifest": retriever.manifest,
        } | extra, note=args.note)
        save_run(config, summary, rows, to_markdown(config["run_id"], config, summary, rows))
        print(f"run {config['run_id']}")
        s = summary["all"]
        for rule in RULES:
            cells = "  ".join(f"{m} {format_metric(s[rule], m):<13}" for m in metric_names)
            print(f"{name:<13} {rule:<8} {cells}")


def main() -> None:
    settings = get_settings()
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default=settings.index_name)
    parser.add_argument("--modes", nargs="+", choices=MODES,
                        help="retrieval: default all modes; --judge: default the app's mode")
    parser.add_argument("--questions", type=Path, default=EVAL_DIR / "questions.jsonl")
    parser.add_argument("--limit", type=int, help="only the first N questions (quick runs)")
    parser.add_argument(
        "--neighbours", action=argparse.BooleanOptionalAction, default=None,
        help="add each hit's same-section neighbours (retrieval: default off; --judge: app default)",
    )
    parser.add_argument(
        "--expand", action=argparse.BooleanOptionalAction, default=None,
        help="add LLM-written search queries (retrieval: default off; --judge: app default)",
    )
    parser.add_argument("--judge", action="store_true", help="answer eval with an LLM judge (Phase 7)")
    parser.add_argument("--judge-model", help="override GEMINI_JUDGE_MODEL for this run")
    parser.add_argument("--sleep", type=float, default=6.0,
                        help="seconds to wait after a question that called the API")
    parser.add_argument("--note", default="", help="short label shown in the results table")
    args = parser.parse_args()

    retriever = Retriever(args.index, settings=settings)
    if args.judge:
        args.modes = args.modes or [settings.answer_mode]
        args.neighbours = settings.answer_neighbours if args.neighbours is None else args.neighbours
        args.expand = settings.expand_queries if args.expand is None else args.expand
        for mode in args.modes:
            run_answer_eval(args, settings, retriever, mode)
    else:
        args.modes = args.modes or list(MODES)
        args.neighbours = bool(args.neighbours)
        args.expand = bool(args.expand)
        run_retrieval_eval(args, settings, retriever)
    print(f"Comparison table: {RESULTS_DIR / 'README.md'}")


if __name__ == "__main__":
    main()
