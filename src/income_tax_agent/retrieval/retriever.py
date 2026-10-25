"""One entry point for retrieval: retrieve(query, mode, k).

Modes:
- "dense":  embedding similarity (Chroma)
- "bm25":   keyword match
- "hybrid": both, merged with Reciprocal Rank Fusion
"""

from dataclasses import dataclass
from functools import lru_cache

from langchain_core.embeddings import Embeddings

from income_tax_agent.config import Settings, get_settings
from income_tax_agent.index import load_index
from income_tax_agent.ingest.chunkers.base import Chunk
from income_tax_agent.retrieval.bm25 import BM25Retriever
from income_tax_agent.retrieval.dense import DenseRetriever
from income_tax_agent.retrieval.fusion import FUSIONS, reciprocal_rank_fusion
from income_tax_agent.retrieval.rerank import Reranker, get_reranker

MODES = ("dense", "bm25", "hybrid")


@dataclass
class Hit:
    chunk: Chunk
    score: float  # only comparable within one mode
    rank: int  # 1 = best. A neighbour gets the rank of the hit it was added for.
    neighbour_of: str | None = None  # chunk_id of that hit, for neighbours only


class Retriever:
    def __init__(
        self,
        index_name: str,
        embeddings: Embeddings | None = None,
        settings: Settings | None = None,
        reranker: Reranker | None = None,
    ):
        self.settings = settings or get_settings()
        chunks, store, self.manifest = load_index(index_name, embeddings, self.settings)
        self.chunks = {c.chunk_id: c for c in chunks}
        self._order = chunks  # document order, for neighbour lookups
        self._position = {c.chunk_id: i for i, c in enumerate(chunks)}
        self.dense = DenseRetriever(store)
        self.bm25 = BM25Retriever(chunks)
        # None = settings.rerank decides. Pass one to share a loaded model between indexes.
        if reranker is None and self.settings.rerank:
            reranker = get_reranker(self.settings)
        self.reranker = reranker

    def retrieve(self, query: str, mode: str = "hybrid", k: int = 5) -> list[Hit]:
        if mode == "dense":
            ranked = self.dense.search(query, k)
        elif mode == "bm25":
            ranked = self.bm25.search(query, k)
        elif mode == "hybrid":
            # Fuse deeper lists than k: a chunk ranked 12th by both can beat one ranked
            # 1st by only one of them.
            n = max(k, self.settings.hybrid_candidates)
            dense_ids = [cid for cid, _ in self.dense.search(query, n)]
            bm25_ids = [cid for cid, _ in self.bm25.search(query, n)]
            ranked = reciprocal_rank_fusion([dense_ids, bm25_ids], k=self.settings.rrf_k)[:k]
        else:
            raise ValueError(f"Unknown mode {mode!r}. Use one of {MODES}.")
        return [Hit(self.chunks[cid], score, rank) for rank, (cid, score) in enumerate(ranked, start=1)]

    def retrieve_multi(
        self, queries: list[str], mode: str = "hybrid", k: int = 5, rerank: bool | None = None
    ) -> list[Hit]:
        """Search with several phrasings of one question; merge the lists with RRF.

        One query gives exactly retrieve()'s result, so runs without expansion are unchanged.
        With reranking, the lists are pooled and reordered by the reranker instead (see
        rerank()). `rerank`: None = use it if this retriever has one (settings.rerank).
        """
        if rerank is None:
            rerank = self.reranker is not None
        if rerank:
            return self.rerank(queries, mode, k)
        if len(queries) == 1:
            return self.retrieve(queries[0], mode, k)
        if self.settings.expand_fusion not in FUSIONS:
            raise ValueError(f"Unknown expand_fusion {self.settings.expand_fusion!r}. Use one of {list(FUSIONS)}.")
        n = max(k, self.settings.expand_candidates)
        rankings = [[h.chunk.chunk_id for h in self.retrieve(q, mode, n)] for q in queries]
        fused = FUSIONS[self.settings.expand_fusion](rankings, k=self.settings.rrf_k)[:k]
        return [Hit(self.chunks[cid], score, rank) for rank, (cid, score) in enumerate(fused, start=1)]

    def rerank(self, queries: list[str], mode: str, k: int) -> list[Hit]:
        """Pool the top candidates of every query, then order them by the reranker's score.

        Score = score against the user's question + w * best score against any rewrite.
        The question keeps the user's key words: the rewrites of "tax laws for non-resident
        Indians" all dropped "Indian", and ranked by them alone Section 6 beat 212-217.
        The rewrites bring the Act's wording: "Can I accept 3 lakh in cash?" shares no words
        with "two lakh rupees or more ... otherwise than by an account payee cheque".
        Either one alone lost one of those two questions (eval/results, 2026-10-24).
        The reranker reads search_text, so it also sees the section title in the prefix.
        """
        pool: dict[str, Chunk] = {}
        for q in queries:
            for h in self.retrieve(q, mode, self.settings.rerank_candidates):
                pool.setdefault(h.chunk.chunk_id, h.chunk)
        if not pool:
            return []
        if self.reranker is None:  # switched on per request (app toggle) with settings.rerank off
            self.reranker = get_reranker(self.settings)
        chunks = list(pool.values())
        texts = [c.search_text for c in chunks]
        scores = self.reranker.score(queries[0], texts)
        if len(queries) > 1:
            per_rewrite = [self.reranker.score(q, texts) for q in queries[1:]]
            w = self.settings.rerank_rewrite_weight
            scores = [s + w * max(col) for s, col in zip(scores, zip(*per_rewrite))]
        # Stable sort: equal scores keep search order.
        ranked = sorted(zip(chunks, scores), key=lambda cs: cs[1], reverse=True)[:k]
        return [Hit(c, s, rank) for rank, (c, s) in enumerate(ranked, start=1)]

    def expand_neighbours(self, hits: list[Hit]) -> list[Hit]:
        """Add the previous and next chunk of each hit, if they share a section with it.

        A fixed-size chunk often cuts a table or list in half; the neighbour holds the rest.
        Output order: for each hit by rank, [previous, hit, next]. No chunk appears twice;
        a hit that was already added as a neighbour of a better hit keeps that place.
        """
        out: list[Hit] = []
        seen: set[str] = set()

        def add(hit: Hit) -> None:
            if hit.chunk.chunk_id not in seen:
                seen.add(hit.chunk.chunk_id)
                out.append(hit)

        for hit in hits:
            pos = self._position[hit.chunk.chunk_id]
            sections = set(hit.chunk.sections)
            neighbours = [self._order[i] for i in (pos - 1, pos + 1) if 0 <= i < len(self._order)]
            same_section = [c for c in neighbours if sections & set(c.sections)]
            before = [c for c in same_section if self._position[c.chunk_id] < pos]
            after = [c for c in same_section if self._position[c.chunk_id] > pos]
            for c in before:
                add(Hit(c, hit.score, hit.rank, neighbour_of=hit.chunk.chunk_id))
            add(hit)
            for c in after:
                add(Hit(c, hit.score, hit.rank, neighbour_of=hit.chunk.chunk_id))
        return out


@lru_cache
def get_retriever(index_name: str) -> Retriever:
    """Load an index once per process (the app and the eval call retrieve() many times)."""
    return Retriever(index_name)


def retrieve(query: str, mode: str = "hybrid", k: int = 5, index_name: str | None = None) -> list[Hit]:
    return get_retriever(index_name or get_settings().index_name).retrieve(query, mode, k)
