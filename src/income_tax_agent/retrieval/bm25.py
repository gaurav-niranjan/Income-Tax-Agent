"""Keyword retrieval with BM25. Good at exact terms: section numbers, amounts, defined words."""

import re

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
        # search_text = optional prefix (e.g. "Section 202: <title>") + text.
        self.bm25 = BM25Okapi([tokenize(c.search_text) for c in chunks])

    def search(self, query: str, k: int) -> list[tuple[str, float]]:
        """Top-k (chunk_id, score), best first. Chunks sharing no word are left out."""
        tokens = tokenize(query)
        scores = self.bm25.get_scores(tokens)
        # Check shared words directly: a score of 0 does not mean "no match" (in a tiny
        # corpus, or for very common words, IDF can be 0).
        matching = [i for i, freqs in enumerate(self.bm25.doc_freqs) if any(t in freqs for t in tokens)]
        top = sorted(matching, key=lambda i: -scores[i])[:k]
        return [(self.chunk_ids[i], float(scores[i])) for i in top]
