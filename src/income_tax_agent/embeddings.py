"""Embedding models behind LangChain's `Embeddings` interface.

We wrap fastembed ourselves instead of using `langchain-community` (which is being sunset).
fastembed runs ONNX models locally: no PyTorch, no API key, no rate limits.
"""

import hashlib
import math
from pathlib import Path

from langchain_core.embeddings import Embeddings

from income_tax_agent.config import Settings, get_settings

# BGE's recommended instruction for short queries that search longer passages.
# Passages get no prefix.
BGE_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


def short_model_name(model_name: str) -> str:
    """"BAAI/bge-base-en-v1.5" -> "bge-base". Used in index folder names."""
    name = model_name.split("/")[-1]
    return name.removesuffix("-en-v1.5")


class FastEmbedEmbeddings(Embeddings):
    def __init__(
        self,
        model_name: str = "BAAI/bge-base-en-v1.5",
        cache_dir: Path | None = None,
        query_prefix: str = BGE_QUERY_PREFIX,
        batch_size: int = 16,  # Fastest on an M2 Pro (scripts/benchmark_embed.py).
    ):
        from fastembed import TextEmbedding  # Imported here so FAKE_MODELS runs never load it.

        self.model_name = model_name
        self.query_prefix = query_prefix
        self.batch_size = batch_size
        self._model = TextEmbedding(model_name, cache_dir=str(cache_dir) if cache_dir else None)
        self._counter = None

    @property
    def dim(self) -> int:
        return self._model.embedding_size

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.passage_embed(texts, batch_size=self.batch_size)
        return [v.tolist() for v in vectors]

    def embed_query(self, text: str) -> list[float]:
        return next(iter(self._model.embed([self.query_prefix + text]))).tolist()

    def count_tokens(self, texts: list[str]) -> list[int]:
        """Token count per text, including [CLS] and [SEP], *without* truncation.

        fastembed's own tokenizer cuts at 512 tokens, which would hide exactly the chunks
        we want to find (BGE ignores everything past 512). So we use an untruncated copy.
        """
        if self._counter is None:
            from tokenizers import Tokenizer

            self._counter = Tokenizer.from_str(self._model.model.tokenizer.to_str())
            self._counter.no_truncation()
            self._counter.no_padding()
        return [len(e.ids) for e in self._counter.encode_batch(texts)]

    def config(self) -> dict:
        return {
            "type": "fastembed",
            "model": self.model_name,
            "dim": self.dim,
            "query_prefix": self.query_prefix,
        }


class FakeEmbeddings(Embeddings):
    """Deterministic hash-based vectors for tests and CI. No model download.

    Texts that share words get similar vectors (a bag of hashed words), so simple
    retrieval tests still behave sensibly.
    """

    def __init__(self, dim: int = 64):
        self.model_name = "fake"
        self.dim = dim

    def _vector(self, text: str) -> list[float]:
        v = [0.0] * self.dim
        for word in text.lower().split():
            h = int(hashlib.md5(word.encode()).hexdigest(), 16)
            v[h % self.dim] += 1.0
        norm = math.sqrt(sum(x * x for x in v))
        return [x / norm for x in v] if norm else v

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vector(text)

    def count_tokens(self, texts: list[str]) -> list[int]:
        return [len(t.split()) + 2 for t in texts]

    def config(self) -> dict:
        return {"type": "fake", "model": "fake", "dim": self.dim}


def get_embeddings(settings: Settings | None = None) -> FastEmbedEmbeddings | FakeEmbeddings:
    settings = settings or get_settings()
    if settings.fake_models:
        return FakeEmbeddings()
    return FastEmbedEmbeddings(
        settings.embedding_model,
        cache_dir=settings.model_cache_dir,
        query_prefix=settings.embedding_query_prefix,
    )
