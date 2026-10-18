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
from income_tax_agent.retrieval.fusion import reciprocal_rank_fusion

MODES = ("dense", "bm25", "hybrid")


@dataclass
class Hit:
    chunk: Chunk
    score: float  # only comparable within one mode
    rank: int  # 1 = best


class Retriever:
    def __init__(
        self,
        index_name: str,
        embeddings: Embeddings | None = None,
        settings: Settings | None = None,
    ):
        self.settings = settings or get_settings()
        chunks, store, self.manifest = load_index(index_name, embeddings, self.settings)
        self.chunks = {c.chunk_id: c for c in chunks}
        self.dense = DenseRetriever(store)
        self.bm25 = BM25Retriever(chunks)

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


@lru_cache
def get_retriever(index_name: str) -> Retriever:
    """Load an index once per process (the app and the eval call retrieve() many times)."""
    return Retriever(index_name)


def retrieve(query: str, mode: str = "hybrid", k: int = 5, index_name: str | None = None) -> list[Hit]:
    return get_retriever(index_name or get_settings().index_name).retrieve(query, mode, k)
