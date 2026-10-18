"""Fixed chunker + index build, with fake embeddings (no model download)."""

import json

from helpers import make_page

from income_tax_agent.config import Settings
from income_tax_agent.embeddings import FakeEmbeddings, short_model_name
from income_tax_agent.index import build_index, load_index
from income_tax_agent.ingest.chunkers.fixed import FixedSizeChunker
from income_tax_agent.ingest.sections import build_document

WORDS = " ".join(f"word{i}" for i in range(60))  # ~470 chars of filler
TEXT = (
    "Short title.\n1. (1) This Act " + WORDS + "\n"
    "Definitions.\n2. (1) In this Act " + WORDS + "\n" + WORDS
)


def test_chunks_cover_text_with_overlap_and_whole_words():
    doc = build_document([{"page": 7, "text": TEXT}])
    chunks = FixedSizeChunker(size=300, overlap=50).chunk(doc)

    assert chunks[0].chunk_id == "fixed-300-50:000000"
    assert all(len(c.text) <= 300 for c in chunks)
    # Every chunk starts and ends on a whole word.
    words = set(TEXT.split())
    assert all(c.text.split()[0] in words and c.text.split()[-1] in words for c in chunks)
    # Consecutive chunks overlap.
    for a, b in zip(chunks, chunks[1:]):
        assert a.extra["end"] > b.extra["start"]
    # The last character of the text is in the last chunk.
    assert chunks[-1].extra["end"] == len(doc.text)


def test_chunk_crossing_a_section_boundary_lists_both():
    doc = build_document([{"page": 7, "text": TEXT}])
    chunks = FixedSizeChunker(size=300, overlap=50).chunk(doc)
    for c in chunks:
        if "word59\nDefinitions." in c.text:  # This chunk spans the end of 1 and start of 2.
            assert c.sections == ["1", "2"]
            assert c.section_titles == ["Short title.", "Definitions."]
    assert {tuple(c.sections) for c in chunks} == {("1",), ("1", "2"), ("2",)}


def test_short_model_name():
    assert short_model_name("BAAI/bge-base-en-v1.5") == "bge-base"
    assert short_model_name("BAAI/bge-small-en-v1.5") == "bge-small"


def test_build_and_load_index(tmp_path):
    settings = Settings(index_dir=tmp_path, _env_file=None)
    pages = [make_page(1, "    " + TEXT.replace("\n", "\n    "))]
    out = build_index(FixedSizeChunker(300, 50), FakeEmbeddings(), settings, pages=pages)

    assert out.name == "fixed-300-50__fake"
    manifest = json.loads((out / "manifest.json").read_text())
    assert manifest["chunker"] == {"type": "fixed", "size": 300, "overlap": 50}
    assert manifest["stats"]["tokens"]["over_512"] == 0

    chunks, store, _ = load_index(out.name, FakeEmbeddings(), settings)
    assert len(chunks) == manifest["stats"]["n_chunks"] > 1
    assert all("tokens" in c.extra for c in chunks)
    hit = store.similarity_search("Definitions In this Act", k=1)[0]
    assert hit.metadata["chunk_id"] in {c.chunk_id for c in chunks}
