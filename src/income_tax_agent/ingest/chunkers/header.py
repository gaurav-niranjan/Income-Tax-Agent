"""Wrap another chunker: same chunks, plus a "Section N: <title>" line for embedding.

A chunk from the middle of a section often never names it. The slab-table chunk of
Section 202, for example, does not contain "new tax regime". The prefix gives the
embedding that context. Only the embedding sees it: BM25 and the LLM get the plain text,
so this change measures one thing.
"""

from dataclasses import dataclass, replace

from income_tax_agent.ingest.chunkers.base import Chunk, Chunker
from income_tax_agent.ingest.sections import Document


def section_header(numbers: list[str], titles: list[str]) -> str:
    """"Section 202: New tax regime ...", one line per section ("Schedule XV: ..." as is)."""
    lines = []
    for number, title in zip(numbers, titles):
        label = number if number.startswith("Schedule") else f"Section {number}"
        lines.append(f"{label}: {title}" if title else label)
    return "\n".join(lines)


@dataclass
class HeaderPrefixChunker:
    inner: Chunker

    @property
    def name(self) -> str:
        return f"{self.inner.name}-header"

    def config(self) -> dict:
        return {**self.inner.config(), "embed_prefix": "section header"}

    def chunk(self, doc: Document) -> list[Chunk]:
        out = []
        for c in self.inner.chunk(doc):
            number = c.chunk_id.rsplit(":", 1)[1]
            prefix = section_header(c.sections, c.section_titles)
            out.append(
                replace(
                    c,
                    chunk_id=f"{self.name}:{number}",
                    extra={**c.extra, "embed_prefix": prefix + "\n" if prefix else ""},
                )
            )
        return out
