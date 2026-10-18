"""Ask the Act a question from the command line.

Run: uv run python scripts/ask.py "What is the standard deduction for salary?"
     uv run python scripts/ask.py --ids q01 q19      (questions from eval/questions.jsonl)
"""

import argparse
import json
from pathlib import Path

from income_tax_agent.config import get_settings
from income_tax_agent.graph.build import build_graph
from income_tax_agent.llm import get_llm
from income_tax_agent.retrieval.retriever import MODES, get_retriever

QUESTIONS = Path(__file__).parents[1] / "eval/questions.jsonl"


def main() -> None:
    settings = get_settings()
    parser = argparse.ArgumentParser()
    parser.add_argument("questions", nargs="*")
    parser.add_argument("--ids", nargs="+", default=[], help="eval question ids")
    parser.add_argument("--mode", default=settings.answer_mode, choices=MODES)
    parser.add_argument("--k", type=int, default=settings.answer_k)
    args = parser.parse_args()

    items = [(None, q) for q in args.questions]
    if args.ids:
        by_id = {d["id"]: d for d in map(json.loads, QUESTIONS.read_text().splitlines())}
        items += [(i, by_id[i]["question"]) for i in args.ids]

    llm = get_llm(settings)
    graph = build_graph(get_retriever(settings.index_name), llm)
    for qid, question in items:
        state = graph.invoke({"question": question, "mode": args.mode, "k": args.k})
        print("=" * 80)
        print(f"{qid or ''} Q: {question}")
        print(f"Retrieved ({args.mode}, k={args.k}):")
        for h in state["hits"]:
            print(f"  {h.rank}. sections {', '.join(h.chunk.sections)}  (pages {h.chunk.pages})")
        print(f"\nA: {state['answer']}\n")
        print(f"cited: {state['citations']}  unsupported: {state['unsupported_citations']}  "
              f"refused: {state['refused']}")
    print("=" * 80)
    print(f"model: {llm.model_name}  API calls this run: {getattr(llm, 'api_calls', 0)}")


if __name__ == "__main__":
    main()
