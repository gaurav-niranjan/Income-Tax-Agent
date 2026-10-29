"""Graph nodes. Each takes the state and returns only the keys it changes."""

from income_tax_agent.graph.state import AnswerState
from income_tax_agent.llm import LLM, QuotaExhausted
from income_tax_agent.prompts import (
    ANSWER_SYSTEM,
    NOT_FOUND,
    REWRITE_SYSTEM,
    answer_user_prompt,
    parse_citations,
    parse_rewrite,
    rewrite_user_prompt,
    strip_excerpt_refs,
)
from income_tax_agent.retrieval.expand import expand_query
from income_tax_agent.retrieval.retriever import Retriever


def _question(state: AnswerState) -> str:
    """What is searched and answered: the rewritten follow-up if there is one."""
    return state.get("standalone_question") or state["question"]


def rewrite(state: AnswerState, llm: LLM, history_turns: int) -> AnswerState:
    """Rewrite a follow-up ("And for senior citizens?") so it makes sense on its own."""
    history = state.get("history", [])[-history_turns:] if history_turns > 0 else []
    if not history:  # first question of the chat: no LLM call
        return {"standalone_question": state["question"], "rewrite_error": None}
    try:
        raw = llm.complete(REWRITE_SYSTEM, rewrite_user_prompt(state["question"], history))
        return {"standalone_question": parse_rewrite(raw, state["question"]), "rewrite_error": None}
    except QuotaExhausted:
        raise
    except Exception as e:  # like expansion: fall back to the question as typed
        return {"standalone_question": state["question"], "rewrite_error": str(e)}


def expand(state: AnswerState, llm: LLM) -> AnswerState:
    question = _question(state)
    if not state.get("expand"):
        return {"queries": [question], "expand_error": None}
    try:
        return {"queries": expand_query(question, llm), "expand_error": None}
    except QuotaExhausted:
        raise  # the day's quota is gone; the answer call would fail too, so say so now
    except Exception as e:  # expansion only helps search: on any other error, search the question alone
        return {"queries": [question], "expand_error": str(e)}


def retrieve(state: AnswerState, retriever: Retriever) -> AnswerState:
    queries = state.get("queries") or [_question(state)]
    hits = retriever.retrieve_multi(queries, mode=state["mode"], k=state["k"], rerank=state.get("rerank"))
    if state.get("neighbours"):
        hits = retriever.expand_neighbours(hits)
    return {"hits": hits}


def route_after_retrieve(state: AnswerState) -> str:
    """No chunks at all (e.g. BM25 with no shared words): answer "not found" without the LLM."""
    return "generate" if state["hits"] else "not_found"


def generate(state: AnswerState, llm: LLM) -> AnswerState:
    raw = llm.complete(ANSWER_SYSTEM, answer_user_prompt(_question(state), state["hits"]))
    answer = strip_excerpt_refs(raw).strip()
    citations = parse_citations(answer)
    retrieved = {s for h in state["hits"] for s in h.chunk.sections}
    return {
        "answer": answer,
        # The model may refuse with slightly different wording or punctuation.
        "refused": answer.rstrip(".").lower() == NOT_FOUND.rstrip(".").lower(),
        "citations": citations,
        "unsupported_citations": [c for c in citations if c not in retrieved],
        "history": [{"question": state["question"], "answer": answer}],
    }


def not_found(state: AnswerState) -> AnswerState:
    return {
        "answer": NOT_FOUND, "refused": True, "citations": [], "unsupported_citations": [],
        "history": [{"question": state["question"], "answer": NOT_FOUND}],
    }
