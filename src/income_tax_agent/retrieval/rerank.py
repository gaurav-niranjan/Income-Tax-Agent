"""Rerankers: score (question, chunk) pairs and reorder the candidates search found.

Dense search compares two separate vectors; BM25 counts shared words. A cross-encoder
reads the question and the chunk together, so it can tell that "non-resident Indians" is
about Section 214 ("an assessee, being a non-resident Indian") more than about Section 6
(who is resident at all). It is too slow to run over all ~2,000 chunks, so it only
reorders the few dozen candidates that dense / BM25 / hybrid search returned.

fastembed runs the cross-encoders as ONNX models: no PyTorch, no new dependency.
"""

import re
from pathlib import Path
from typing import Protocol

from income_tax_agent.config import Settings, get_settings


class Reranker(Protocol):
    model_name: str

    def score(self, query: str, texts: list[str]) -> list[float]:
        """One relevance score per text; higher = more relevant. Only the order matters."""
        ...


class FastEmbedReranker:
    def __init__(
        self, model_name: str, cache_dir: Path | None = None, batch_size: int = 16, model_dir: Path | None = None
    ):
        from fastembed.rerank.cross_encoder import TextCrossEncoder  # FAKE_MODELS runs never load it

        self.model_name = model_name
        self.batch_size = batch_size
        # model_dir: load from that folder as-is (Vercel: read-only, no download).
        options = {"specific_model_path": str(model_dir)} if model_dir else {}
        self._model = TextCrossEncoder(model_name, cache_dir=str(cache_dir) if cache_dir else None, **options)

    def score(self, query: str, texts: list[str]) -> list[float]:
        return [float(s) for s in self._model.rerank(query, texts, batch_size=self.batch_size)]


class FakeReranker:
    """Share of the query's words found in the text. For tests and CI: no download."""

    model_name = "fake"

    def score(self, query: str, texts: list[str]) -> list[float]:
        words = set(re.findall(r"[a-z0-9]+", query.lower()))
        return [len(words & set(re.findall(r"[a-z0-9]+", t.lower()))) / (len(words) or 1) for t in texts]


def get_reranker(settings: Settings | None = None) -> Reranker:
    settings = settings or get_settings()
    if settings.fake_models:
        return FakeReranker()
    return FastEmbedReranker(
        settings.rerank_model, cache_dir=settings.model_cache_dir, model_dir=settings.rerank_model_dir
    )
