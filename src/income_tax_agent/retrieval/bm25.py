"""Keyword retrieval with BM25. Good at exact terms: section numbers, amounts, defined words."""

import re

import numpy as np
from rank_bm25 import BM25Okapi

from income_tax_agent.ingest.chunkers.base import Chunk

TOKEN_RE = re.compile(r"[a-z0-9]+")
# "Rs. 20,000" and a query with "20000" should match, so drop commas inside numbers.
DIGIT_COMMA_RE = re.compile(r"(?<=\d),(?=\d)")


def tokenize(text: str) -> list[str]:
    """Lowercase words and numbers. "section 2(77)(g)" -> ["section", "2", "77", "g"]."""
    return TOKEN_RE.findall(DIGIT_COMMA_RE.sub("", text.lower()))


class BM25Retriever:
    def __init__(self, chunks: list[Chunk]):
        self.chunk_ids = [c.chunk_id for c in chunks]
        # Built in memory on load: ~2k chunks take well under a second.
        self.bm25 = BM25Okapi([tokenize(c.text) for c in chunks])

    def search(self, query: str, k: int) -> list[tuple[str, float]]:
        """Top-k (chunk_id, score), best first. Chunks sharing no word are left out."""
        scores = self.bm25.get_scores(tokenize(query))
        top = np.argsort(-scores)[:k]
        return [(self.chunk_ids[i], float(scores[i])) for i in top if scores[i] > 0]
