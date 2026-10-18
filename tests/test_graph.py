"""Answer graph, citation parsing and LLM cache, with fake models only."""

import json

import pytest
from helpers import make_page

from income_tax_agent.config import Settings
from income_tax_agent.embeddings import FakeEmbeddings
from income_tax_agent.graph.build import build_graph
from income_tax_agent.index import build_index
from income_tax_agent.ingest.chunkers.fixed import FixedSizeChunker
from income_tax_agent.llm import FakeLLM, GeminiLLM, NotRetryable, QuotaExhausted
from income_tax_agent.prompts import NOT_FOUND, parse_citations
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


class _Reply:
    def __init__(self, text):
        self.text = text


def _offline_gemini(tmp_path, chat):
    llm = GeminiLLM.__new__(GeminiLLM)  # skip __init__: no key or network needed
    llm.model_name, llm.temperature, llm.cache_dir, llm.api_calls = "m", None, tmp_path, 0
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
