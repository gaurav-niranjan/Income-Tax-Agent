"""Eval metric tests on hand-made chunks."""

import pytest
from metrics import Question, first_hit_ranks, format_metric, is_strict_hit, summarize, summarize_by_type

from income_tax_agent.ingest.chunkers.base import Chunk


def chunk(cid: str, text: str, section_chars: dict[str, int]) -> Chunk:
    return Chunk(cid, text, [1], list(section_chars), [""] * len(section_chars), {"section_chars": section_chars})


Q = Question("q", "table", "rates?", ["202"], ["From Rs. 800001 to Rs. 1200000"], "10%")


def test_strict_hit_needs_30_percent_of_the_chunk():
    assert is_strict_hit(chunk("a", "", {"201": 700, "202": 300}), ["202"])  # exactly 30%
    assert not is_strict_hit(chunk("b", "", {"201": 701, "202": 299}), ["202"])
    assert not is_strict_hit(chunk("c", "", {}), ["202"])


def test_first_hit_ranks_per_rule():
    chunks = [
        chunk("1", "unrelated", {"5": 900}),
        chunk("2", "edge of 202", {"201": 900, "202": 100}),  # section hit, not strict
        chunk("3", "From  Rs. 800001 to\nRs. 1200000  10%", {"202": 950}),  # spacing differs
    ]
    ranked = list(enumerate(chunks, start=1))
    assert first_hit_ranks(ranked, Q) == {"section": 2, "strict": 3, "phrase": 3}
    assert first_hit_ranks(ranked[:1], Q) == {"section": None, "strict": None, "phrase": None}
    # Neighbour expansion: the table chunk arrives as a neighbour of the rank-2 hit.
    expanded = [(1, chunks[0]), (2, chunks[1]), (2, chunks[2])]
    assert first_hit_ranks(expanded, Q) == {"section": 2, "strict": 2, "phrase": 2}


def test_summarize_hit_at_k_and_mrr():
    s = summarize([1, 3, None, 6])
    assert s["hit@1"] == 0.25
    assert s["hit@3"] == 0.5
    assert s["hit@5"] == 0.5
    assert (s["n"], s["hits@1"], s["hits@3"], s["hits@5"]) == (4, 1, 2, 2)
    assert s["mrr"] == pytest.approx((1 + 1 / 3 + 0 + 1 / 6) / 4)
    assert format_metric(s, "hit@3") == "0.50 (2/4)"
    assert format_metric(s, "mrr") == "0.38"


def test_summarize_by_type_has_all_group_and_per_type_counts():
    rows = [
        {"type": "table", "ranks": {"section": 1, "strict": 1, "phrase": None}},
        {"type": "lakh", "ranks": {"section": None, "strict": None, "phrase": None}},
        {"type": "table", "ranks": {"section": 2, "strict": 4, "phrase": 2}},
    ]
    s = summarize_by_type(rows)
    assert list(s) == ["all", "table", "lakh"]
    assert (s["all"]["n"], s["table"]["n"], s["lakh"]["n"]) == (3, 2, 1)
    assert s["table"]["section"]["hit@1"] == 0.5
    assert s["lakh"]["phrase"]["mrr"] == 0.0
