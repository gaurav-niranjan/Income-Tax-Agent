"""How fast does an embedding model run on this machine? Prints chunks/sec.

Uses real chunks from the Act (fixed 1,000-char windows), so the speed matches what
building the index will see.

Run: uv run python scripts/benchmark_embed.py [--model BAAI/bge-base-en-v1.5] [--n 256]
"""

import argparse
import platform
import time

from income_tax_agent.config import get_settings
from income_tax_agent.embeddings import FastEmbedEmbeddings
from income_tax_agent.ingest.chunkers.fixed import FixedSizeChunker
from income_tax_agent.ingest.clean import clean_pages
from income_tax_agent.ingest.extract import load_pages
from income_tax_agent.ingest.sections import build_document


def main() -> None:
    settings = get_settings()
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=settings.embedding_model)
    parser.add_argument("--n", type=int, default=256, help="number of chunks to embed")
    parser.add_argument("--batch-sizes", type=int, nargs="+", default=[16, 64])
    args = parser.parse_args()

    doc = build_document(clean_pages(load_pages(settings.pages_path)).pages)
    chunks = FixedSizeChunker(settings.chunk_size, settings.chunk_overlap).chunk(doc)
    # Spread the sample over the whole Act: prose, definitions and tables.
    step = max(len(chunks) // args.n, 1)
    texts = [c.text for c in chunks[::step][: args.n]]

    t0 = time.perf_counter()
    model = FastEmbedEmbeddings(args.model, cache_dir=settings.model_cache_dir)
    print(f"Model: {args.model}  (load time {time.perf_counter() - t0:.1f}s, includes download on first run)")
    print(f"Machine: {platform.machine()} / {platform.processor() or '?'} / {platform.platform()}")
    model.embed_documents(texts[:8])  # Warm-up: the first call pays one-off setup costs.

    for batch_size in args.batch_sizes:
        model.batch_size = batch_size
        t0 = time.perf_counter()
        model.embed_documents(texts)
        rate = len(texts) / (time.perf_counter() - t0)
        print(
            f"batch_size={batch_size:<4} {rate:6.1f} chunks/sec  -> "
            f"all {len(chunks):,} chunks in ~{len(chunks) / rate:.0f}s"
        )


if __name__ == "__main__":
    main()
