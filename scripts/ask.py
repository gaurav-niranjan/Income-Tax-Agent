"""Ask the Act a question from the command line.

Run: uv run python scripts/ask.py "What is the standard deduction for salary?"
     uv run python scripts/ask.py --ids q01 q19      (questions from eval/questions.jsonl)
"""

import argparse
import json
from pathlib import Path

from income_tax_agent.config import get_settings
from income_tax_agent.graph.build import build_graph
from income_tax_agent.llm import get_expand_llm, get_llm
from income_tax_agent.retrieval.retriever import MODES, get_retriever

QUESTIONS = Path(__file__).parents[1] / "eval/questions.jsonl"


def main() -> None:
    settings = get_settings()
    parser = argparse.ArgumentParser()
    parser.add_argument("questions", nargs="*")
    parser.add_argument("--ids", nargs="+", default=[], help="eval question ids")
    parser.add_argument("--mode", default=settings.answer_mode, choices=MODES)
    parser.add_argument("--k", type=int, default=settings.answer_k)
    parser.add_argument("--index", default=settings.index_name)
    parser.add_argument(
        "--neighbours", action=argparse.BooleanOptionalAction, default=settings.answer_neighbours
    )
    parser.add_argument("--expand", action=argparse.BooleanOptionalAction, default=settings.expand_queries)
    args = parser.parse_args()

    items = [(None, q) for q in args.questions]
    if args.ids:
        by_id = {d["id"]: d for d in map(json.loads, QUESTIONS.read_text().splitlines())}
        items += [(i, by_id[i]["question"]) for i in args.ids]

    llm, expand_llm = get_llm(settings), get_expand_llm(settings)
    graph = build_graph(get_retriever(args.index), llm, expand_llm)
    for qid, question in items:
        state = graph.invoke(
            {"question": question, "mode": args.mode, "k": args.k, "neighbours": args.neighbours,
             "expand": args.expand}
        )
        print("=" * 80)
        print(f"{qid or ''} Q: {question}")
        nb = ", +neighbours" if args.neighbours else ""
        for q in state["queries"][1:]:
            print(f"Also searched: {q}")
        if state.get("expand_error"):
            print(f"Expansion failed, searched the question only: {state['expand_error']}")
        print(f"Retrieved ({args.index}, {args.mode}, k={args.k}{nb}):")
        for h in state["hits"]:
            tag = "   (neighbour)" if h.neighbour_of else ""
            print(f"  {h.rank}. sections {', '.join(h.chunk.sections)}  (pages {h.chunk.pages}){tag}")
        print(f"\nA: {state['answer']}\n")
        print(f"cited: {state['citations']}  unsupported: {state['unsupported_citations']}  "
              f"refused: {state['refused']}")
    print("=" * 80)
    print(f"model: {llm.model_name}  API calls this run: {getattr(llm, 'api_calls', 0)} "
          f"(+{getattr(expand_llm, 'api_calls', 0)} for query expansion, {expand_llm.model_name})")


if __name__ == "__main__":
    main()
