"""Build and load an index. Each index lives in its own folder, named by its config:

    data/index/<chunker>__<embedder>/      e.g. fixed-1000-150__bge-base
        chunks.jsonl    every chunk with its metadata (BM25 and the eval read this)
        chroma/         the vector store
        manifest.json   the full config used to build it, plus stats

Run: uv run python -m income_tax_agent.index [--force]
"""

import argparse
import hashlib
import json
import shutil
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

import chromadb
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

from income_tax_agent.config import Settings, get_settings
from income_tax_agent.embeddings import get_embeddings, short_model_name
from income_tax_agent.ingest.chunkers.base import Chunk, Chunker
from income_tax_agent.ingest.chunkers.fixed import FixedSizeChunker
from income_tax_agent.ingest.clean import clean_pages
from income_tax_agent.ingest.extract import load_pages
from income_tax_agent.ingest.sections import build_document

COLLECTION = "chunks"
BGE_MAX_TOKENS = 512  # BGE silently ignores tokens past this.
EMBED_BATCH = 256  # Chunks per add_texts call, so we can print progress.


def index_name(chunker: Chunker, embeddings: Embeddings) -> str:
    return f"{chunker.name}__{short_model_name(embeddings.model_name)}"


def _chroma(path: Path, embeddings: Embeddings) -> Chroma:
    # Telemetry off: the app should not phone home, and CI has no network guarantees.
    client = chromadb.PersistentClient(
        path=str(path), settings=chromadb.Settings(anonymized_telemetry=False)
    )
    # Default distance is L2. Our vectors are unit length, so L2 ranks exactly like cosine.
    return Chroma(collection_name=COLLECTION, embedding_function=embeddings, client=client)


def _metadata(chunk: Chunk) -> dict:
    # Chroma accepts lists of scalars, but not empty lists.
    meta = {"chunk_id": chunk.chunk_id, "pages": chunk.pages or [0]}
    meta["sections"] = chunk.sections or [""]
    return meta


def token_stats(counts: list[int]) -> dict:
    s = sorted(counts)
    pct = lambda p: s[min(int(p / 100 * len(s)), len(s) - 1)]  # noqa: E731
    return {
        "min": s[0],
        "p50": pct(50),
        "p90": pct(90),
        "p99": pct(99),
        "max": s[-1],
        "mean": round(statistics.mean(s), 1),
        "over_512": sum(c > BGE_MAX_TOKENS for c in s),
    }


def build_index(
    chunker: Chunker,
    embeddings: Embeddings,
    settings: Settings | None = None,
    pages: list[dict] | None = None,
    force: bool = False,
) -> Path:
    """Chunk, count tokens, embed and save. Returns the index folder."""
    settings = settings or get_settings()
    pages = pages if pages is not None else load_pages(settings.pages_path)
    out = settings.index_dir / index_name(chunker, embeddings)
    if out.exists():
        if not force:
            raise FileExistsError(f"{out} exists. Pass force=True (--force) to rebuild it.")
        shutil.rmtree(out)  # An index is always rebuildable from pages.jsonl.
    out.mkdir(parents=True)

    doc = build_document(clean_pages(pages, settings.strip_footnotes).pages)
    chunks = chunker.chunk(doc)

    counts = embeddings.count_tokens([c.text for c in chunks])
    for chunk, n in zip(chunks, counts):
        chunk.extra["tokens"] = n
    stats = token_stats(counts)
    if stats["over_512"]:
        print(f"WARNING: {stats['over_512']} chunks are over {BGE_MAX_TOKENS} tokens; BGE ignores the excess.")

    with (out / "chunks.jsonl").open("w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk.to_dict(), ensure_ascii=False) + "\n")

    store = _chroma(out / "chroma", embeddings)
    t0 = time.perf_counter()
    for i in range(0, len(chunks), EMBED_BATCH):
        batch = chunks[i : i + EMBED_BATCH]
        store.add_texts(
            [c.text for c in batch], metadatas=[_metadata(c) for c in batch], ids=[c.chunk_id for c in batch]
        )
        print(f"  embedded {min(i + EMBED_BATCH, len(chunks))}/{len(chunks)} chunks")
    embed_seconds = time.perf_counter() - t0

    manifest = {
        "name": out.name,
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": {
            "pdf": settings.pdf_path.name,
            # Hash of the extracted text: tells us if two indexes were built from the same input.
            "pages_sha256": hashlib.sha256(
                json.dumps(pages, ensure_ascii=False).encode()
            ).hexdigest()[:16],
            "n_pages": len(pages),
        },
        "cleaning": {"strip_footnotes": settings.strip_footnotes},
        "chunker": chunker.config(),
        "embeddings": embeddings.config(),
        "vector_store": {"type": "chroma", "collection": COLLECTION, "distance": "l2"},
        "stats": {
            "n_chunks": len(chunks),
            "n_chunks_multi_section": sum(len(c.sections) > 1 for c in chunks),
            "chars_total": len(doc.text),
            "tokens": stats,
            "embed_seconds": round(embed_seconds, 1),
        },
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return out


def load_index(name: str, embeddings: Embeddings | None = None, settings: Settings | None = None):
    """Return (chunks, chroma store, manifest) for an existing index folder."""
    settings = settings or get_settings()
    folder = settings.index_dir / name
    manifest = json.loads((folder / "manifest.json").read_text())
    with (folder / "chunks.jsonl").open(encoding="utf-8") as f:
        chunks = [Chunk.from_dict(json.loads(line)) for line in f]
    store = _chroma(folder / "chroma", embeddings or get_embeddings(settings))
    return chunks, store, manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the baseline index.")
    parser.add_argument("--force", action="store_true", help="rebuild if the folder exists")
    args = parser.parse_args()

    settings = get_settings()
    chunker = FixedSizeChunker(settings.chunk_size, settings.chunk_overlap)
    out = build_index(chunker, get_embeddings(settings), settings, force=args.force)
    stats = json.loads((out / "manifest.json").read_text())["stats"]
    print(f"Built {out}")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
