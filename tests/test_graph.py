"""Answer graph, citation parsing and LLM cache, with fake models only."""

import json

import pytest
from helpers import make_page

from income_tax_agent.config import Settings
from income_tax_agent.embeddings import FakeEmbeddings
from income_tax_agent.graph.build import build_graph, memory_checkpointer
from income_tax_agent.index import build_index
from income_tax_agent.ingest.chunkers.fixed import FixedSizeChunker
from income_tax_agent.llm import FakeLLM, GeminiLLM, NotRetryable, QuotaExhausted, record_llm_calls
from income_tax_agent.prompts import NOT_FOUND, parse_citations, parse_expansions, strip_excerpt_refs
from income_tax_agent.retrieval.retriever import Retriever

BODY = """    Short title, extent and commencement.
    1. (1) This Act may be called the Income-tax Act, 2025.
    Deduction in respect of health insurance premia.
    2. (1) A deduction of Rs. 25,000 is allowed for health insurance premium."""


@pytest.fixture(scope="module")
def retriever(tmp_path_factory):
    settings = Settings(index_dir=tmp_path_factory.mktemp("index"), _env_file=None)
    out = build_index(FixedSizeChunker(200, 20), FakeEmbeddings(), settings, pages=[make_page(1, BODY)])
    return Retriever(out.name, FakeEmbeddings(), settings)


@pytest.mark.parametrize(
    "answer, expected",
    [
        ("Rates are in the table [Section 202].", ["202"]),
        ("See [Section 202(1)(a)] and [Section 156(2)].", ["202", "156"]),
        ("[Sections 202 and 156] [Section 202]", ["202", "156"]),
        ("10% [Section 393(1), Table: Sl. No. 2(ii)]", ["393"]),
        ("Listed in [Schedule XV] under [Section 123].", ["Schedule XV", "123"]),
        ("No brackets: Section 202.", []),
    ],
)
def test_parse_citations(answer, expected):
    assert parse_citations(answer) == expected


@pytest.mark.parametrize(
    "raw, expected",
    [
        # Real outputs from the answer eval (q15, q10, q19).
        ("is Rs. 25000 in aggregate [Section 126, Excerpt 4].", "is Rs. 25000 in aggregate [Section 126]."),
        ("means [Excerpt 1, Excerpt 2]:", "means:"),
        ("1. Spouse of the individual [Excerpt 2];", "1. Spouse of the individual;"),
        ("**10%** [Section 202, Excerpt 1 & Excerpt 2]", "**10%** [Section 202]"),
        ("see [Section 92; Excerpts 8 and 9] here", "see [Section 92] here"),
        ("No excerpt refs [Section 202(1)].", "No excerpt refs [Section 202(1)]."),
    ],
)
def test_strip_excerpt_refs(raw, expected):
    assert strip_excerpt_refs(raw) == expected


def test_graph_answers_with_citations(retriever):
    graph = build_graph(retriever, FakeLLM())
    state = graph.invoke({"question": "health insurance premium deduction", "mode": "bm25", "k": 2})
    assert state["hits"]
    assert state["refused"] is False
    assert state["citations"] and not state["unsupported_citations"]


def test_graph_skips_llm_when_nothing_is_retrieved(retriever):
    class ExplodingLLM(FakeLLM):
        def complete(self, system, user):
            raise AssertionError("LLM must not be called")

    graph = build_graph(retriever, ExplodingLLM())
    state = graph.invoke({"question": "zzz qqq", "mode": "bm25", "k": 2})  # no shared words
    assert state["hits"] == []
    assert state["answer"] == NOT_FOUND and state["refused"] is True


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("a b\nc d\ne f", ["a b", "c d", "e f"]),
        ("Here are 3 queries:\n1. a b\n2) c d\n- e f", ["a b", "c d", "e f"]),
        ('"wrapped in quotes"\n"senior citizen" means an individual', ["wrapped in quotes", '"senior citizen" means an individual']),
        ("1.25 lakh = Rs. 125000\n\n\n", ["1.25 lakh = Rs. 125000"]),  # a number is not a list mark
        ("The Question\na b\nA B\nc\nd\ne", ["a b", "c", "d"]),  # repeats dropped, at most 3
    ],
)
def test_parse_expansions(raw, expected):
    assert parse_expansions(raw, "the question") == expected


class ExpandingLLM(FakeLLM):
    """Answers like FakeLLM; for expansion, replies with fixed queries (or raises `error`)."""

    def __init__(self, reply="health insurance premia deduction\nRs. 25000 deduction", error=None):
        self.reply, self.error, self.expand_calls = reply, error, 0

    def complete(self, system, user):
        if user.startswith("Question: "):
            self.expand_calls += 1
            if self.error:
                raise self.error
            return self.reply
        return super().complete(system, user)


def test_graph_without_expand_flag_searches_only_the_question(retriever):
    llm = ExpandingLLM()
    state = build_graph(retriever, FakeLLM(), llm).invoke({"question": "zzz qqq", "mode": "bm25", "k": 2})
    assert state["queries"] == ["zzz qqq"] and llm.expand_calls == 0


def test_graph_expansion_finds_what_the_question_alone_misses(retriever):
    graph = build_graph(retriever, FakeLLM(), ExpandingLLM())
    # No word of "zzz qqq" is in the Act, so BM25 alone finds nothing; the expansions do.
    state = graph.invoke({"question": "zzz qqq", "mode": "bm25", "k": 2, "expand": True})
    assert state["queries"] == ["zzz qqq", "health insurance premia deduction", "Rs. 25000 deduction"]
    assert state["hits"] and "2" in state["hits"][0].chunk.sections
    assert state["refused"] is False


def test_graph_falls_back_to_the_question_when_expansion_fails(retriever):
    graph = build_graph(retriever, FakeLLM(), ExpandingLLM(error=NotRetryable("bad request")))
    state = graph.invoke({"question": "health insurance premium", "mode": "bm25", "k": 2, "expand": True})
    assert state["queries"] == ["health insurance premium"]
    assert "bad request" in state["expand_error"]
    assert state["hits"] and state["answer"]


def test_graph_stops_when_expansion_quota_is_gone(retriever):
    graph = build_graph(retriever, FakeLLM(), ExpandingLLM(error=QuotaExhausted("daily quota")))
    with pytest.raises(QuotaExhausted):
        graph.invoke({"question": "health insurance", "mode": "bm25", "k": 2, "expand": True})


def _chat(graph, question, thread="t1", **inputs):
    return graph.invoke({"question": question, "mode": "bm25", "k": 2, **inputs},
                        config={"configurable": {"thread_id": thread}})


def test_follow_up_is_rewritten_with_the_chat_history(retriever):
    llm = FakeLLM()
    graph = build_graph(retriever, llm, checkpointer=memory_checkpointer(), history_turns=3)
    with record_llm_calls() as calls:
        first = _chat(graph, "health insurance premium deduction")
    assert first["standalone_question"] == "health insurance premium deduction"
    assert len(calls) == 1  # only the answer: no history, so no rewrite call

    # FakeLLM's rewrite puts the previous question in front of the follow-up.
    second = _chat(graph, "and the limit?")
    assert second["standalone_question"] == "health insurance premium deduction and the limit?"
    assert second["queries"][0] == second["standalone_question"]
    assert [t["question"] for t in second["history"]] == ["health insurance premium deduction", "and the limit?"]

    other = _chat(graph, "and the limit?", thread="t2")  # another visitor: no shared memory
    assert other["standalone_question"] == "and the limit?" and len(other["history"]) == 1


def test_errors_are_not_left_over_from_the_previous_question(retriever):
    graph = build_graph(retriever, FakeLLM(), ExpandingLLM(error=NotRetryable("bad request")),
                        checkpointer=memory_checkpointer(), history_turns=0)
    first = _chat(graph, "health insurance premium", expand=True)
    assert first["expand_error"]
    second = _chat(graph, "short title", expand=False)
    assert second["expand_error"] is None


def test_chat_continues_after_a_failed_question(retriever):
    llm = ExpandingLLM(error=QuotaExhausted("daily quota"))
    graph = build_graph(retriever, FakeLLM(), llm, checkpointer=memory_checkpointer())
    with pytest.raises(QuotaExhausted):
        _chat(graph, "health insurance", expand=True)
    llm.error = None
    state = _chat(graph, "health insurance premium", expand=False)
    assert state["answer"] and [t["question"] for t in state["history"]] == ["health insurance premium"]


class _Reply:
    def __init__(self, text, usage_metadata=None):
        self.text, self.usage_metadata = text, usage_metadata


def test_llm_calls_are_logged_with_tokens_and_cache_hits(tmp_path):
    usage = {"input_tokens": 100, "output_tokens": 30, "total_tokens": 130, "output_token_details": {"reasoning": 20}}

    class Chat:
        def invoke(self, messages):
            return _Reply("answer", usage)

    llm = _offline_gemini(tmp_path, Chat())
    with record_llm_calls() as calls:
        llm.complete("sys", "q")
        llm.complete("sys", "q")
    llm.complete("sys", "q")  # outside the block: not logged
    assert [c["cached"] for c in calls] == [False, True]
    # A cache hit shows what the call cost the first time.
    assert calls[0]["usage"] == calls[1]["usage"] == {"input": 100, "output": 30, "thinking": 20, "total": 130}
    assert calls[0]["user"] == "q" and calls[0]["reply"] == "answer"


def _offline_gemini(tmp_path, chat):
    llm = GeminiLLM.__new__(GeminiLLM)  # skip __init__: no key or network needed
    llm.model_name, llm.temperature, llm.thinking_level, llm.cache_dir, llm.api_calls = "m", None, None, tmp_path, 0
    llm._chat = chat
    return llm


def test_llm_cache_avoids_second_call(tmp_path):
    class Chat:
        calls = 0

        def invoke(self, messages):
            Chat.calls += 1
            return _Reply("answer")

    llm = _offline_gemini(tmp_path, Chat())
    assert llm.complete("sys", "q") == "answer"
    assert llm.complete("sys", "q") == "answer"
    assert Chat.calls == 1
    assert json.loads(next(tmp_path.glob("*.json")).read_text())["text"] == "answer"
    llm.complete("sys", "a different question")
    assert Chat.calls == 2


def test_llm_without_cache_calls_every_time(tmp_path):
    class Chat:
        calls = 0

        def invoke(self, messages):
            Chat.calls += 1
            return _Reply("answer")

    llm = _offline_gemini(tmp_path, Chat())
    llm.cache_dir = None
    llm.complete("sys", "q")
    llm.complete("sys", "q")
    assert Chat.calls == 2 and not list(tmp_path.iterdir())


def test_llm_stops_at_once_on_daily_quota(tmp_path):
    from langchain_google_genai.chat_models import GoogleRateLimitError

    class Chat:
        calls = 0

        def invoke(self, messages):
            Chat.calls += 1
            raise GoogleRateLimitError("429 RESOURCE_EXHAUSTED quotaId: GenerateRequestsPerDayPerProjectPerModel-FreeTier")

    llm = _offline_gemini(tmp_path, Chat())
    with pytest.raises(QuotaExhausted):
        llm.complete("sys", "q")
    assert Chat.calls == 1  # no pointless retries


def test_llm_does_not_retry_permanent_errors(tmp_path):
    class Chat:
        calls = 0

        def invoke(self, messages):
            Chat.calls += 1
            raise ValueError("API key not valid")

    llm = _offline_gemini(tmp_path, Chat())
    with pytest.raises(NotRetryable):
        llm.complete("sys", "q")
    assert Chat.calls == 1
