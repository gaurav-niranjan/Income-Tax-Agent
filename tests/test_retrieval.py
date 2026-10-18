"""Retrieval tests on a tiny index built with fake embeddings."""

import pytest
from helpers import make_page

from income_tax_agent.config import Settings
from income_tax_agent.embeddings import FakeEmbeddings
from income_tax_agent.index import build_index
from income_tax_agent.ingest.chunkers.fixed import FixedSizeChunker
from income_tax_agent.ingest.chunkers.base import Chunk
from income_tax_agent.retrieval.bm25 import BM25Retriever, tokenize
from income_tax_agent.retrieval.fusion import reciprocal_rank_fusion
from income_tax_agent.retrieval.retriever import Hit, Retriever

BODY = """    Short title, extent and commencement.
    1. (1) This Act may be called the Income-tax Act, 2025. It extends to the whole of India.
    Deduction in respect of health insurance premia.
    2. (1) A deduction of Rs. 25,000 is allowed for health insurance premium paid by an individual.
    Tax to be deducted at source.
    3. (1) Any person paying rent shall deduct income-tax at the rate of 2% on rent."""


@pytest.fixture(scope="module")
def retriever(tmp_path_factory):
    settings = Settings(index_dir=tmp_path_factory.mktemp("index"), _env_file=None)
    out = build_index(FixedSizeChunker(120, 20), FakeEmbeddings(), settings, pages=[make_page(1, BODY)])
    return Retriever(out.name, FakeEmbeddings(), settings)


def test_tokenize_keeps_numbers_and_drops_digit_commas():
    assert tokenize("Rs. 25,000 under section 2(77)(g).") == ["rs", "25000", "under", "section", "2", "77", "g"]


def test_rrf_rewards_items_ranked_by_both_lists():
    fused = reciprocal_rank_fusion([["a", "b", "c"], ["d", "b", "e"]], k=60)
    ids = [i for i, _ in fused]
    assert ids[0] == "b"  # rank 2 in both beats rank 1 in one list
    assert set(ids) == {"a", "b", "c", "d", "e"}
    assert fused[0][1] == pytest.approx(2 / 62)


def test_bm25_finds_exact_amount(retriever):
    hits = retriever.retrieve("deduction of 25000 for health insurance", mode="bm25", k=1)
    assert "25,000" in hits[0].chunk.text and "2" in hits[0].chunk.sections
    assert hits[0].rank == 1


@pytest.mark.parametrize("mode", ["dense", "bm25", "hybrid"])
def test_every_mode_returns_ranked_chunks(retriever, mode):
    hits = retriever.retrieve("rent deduct income-tax 2%", mode=mode, k=3)
    assert 1 <= len(hits) <= 3
    assert [h.rank for h in hits] == list(range(1, len(hits) + 1))
    assert len({h.chunk.chunk_id for h in hits}) == len(hits)


def test_bm25_searches_the_prefix_but_returns_plain_text():
    chunks = [
        Chunk("a:0", "Upto Rs. 400000 Nil", [1], ["202"], ["New tax regime"], {"search_prefix": "Section 202: New tax regime\n"}),
        Chunk("a:1", "Some other rule", [2], ["5"], ["Other"], {}),
    ]
    hit = BM25Retriever(chunks).search("new regime", k=1)
    assert hit[0][0] == "a:0"  # found only through the prefix
    assert chunks[0].text == "Upto Rs. 400000 Nil"


def test_expand_neighbours_adds_same_section_chunks_once(retriever):
    order = retriever._order
    # The test text gives chunks covering sections [1], [1, 2], [2, 3], [3].
    assert [c.sections for c in order] == [["1"], ["1", "2"], ["2", "3"], ["3"]]
    hits = [Hit(order[1], 0.9, 1), Hit(order[2], 0.8, 2)]
    expanded = retriever.expand_neighbours(hits)
    # Hit 1 brings its neighbours 0 and 2; hit 2 is then already present, adds only 3.
    assert [h.chunk.chunk_id for h in expanded] == [c.chunk_id for c in order]
    assert [h.rank for h in expanded] == [1, 1, 1, 2]
    assert [h.neighbour_of for h in expanded] == [order[1].chunk_id, None, order[1].chunk_id, order[2].chunk_id]


def test_expand_neighbours_skips_other_sections(retriever):
    order = retriever._order
    expanded = retriever.expand_neighbours([Hit(order[3], 0.5, 1)])  # section 3 only
    assert [h.chunk.chunk_id for h in expanded] == [order[2].chunk_id, order[3].chunk_id]


def test_unknown_mode_is_an_error(retriever):
    with pytest.raises(ValueError, match="Unknown mode"):
        retriever.retrieve("anything", mode="magic")
