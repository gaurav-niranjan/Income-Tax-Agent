"""Graph nodes. Each takes the state and returns only the keys it changes."""

from income_tax_agent.graph.state import AnswerState
from income_tax_agent.llm import LLM
from income_tax_agent.prompts import ANSWER_SYSTEM, NOT_FOUND, answer_user_prompt, parse_citations
from income_tax_agent.retrieval.retriever import Retriever


def retrieve(state: AnswerState, retriever: Retriever) -> AnswerState:
    return {"hits": retriever.retrieve(state["question"], mode=state["mode"], k=state["k"])}


def route_after_retrieve(state: AnswerState) -> str:
    """No chunks at all (e.g. BM25 with no shared words): answer "not found" without the LLM."""
    return "generate" if state["hits"] else "not_found"


def generate(state: AnswerState, llm: LLM) -> AnswerState:
    answer = llm.complete(ANSWER_SYSTEM, answer_user_prompt(state["question"], state["hits"])).strip()
    citations = parse_citations(answer)
    retrieved = {s for h in state["hits"] for s in h.chunk.sections}
    return {
        "answer": answer,
        # The model may refuse with slightly different wording or punctuation.
        "refused": answer.rstrip(".").lower() == NOT_FOUND.rstrip(".").lower(),
        "citations": citations,
        "unsupported_citations": [c for c in citations if c not in retrieved],
    }


def not_found(state: AnswerState) -> AnswerState:
    return {"answer": NOT_FOUND, "refused": True, "citations": [], "unsupported_citations": []}
