"""Wrap another chunker: same chunks, plus a "Section N: <title>" line for search.

A chunk from the middle of a section often never names it. The slab-table chunk of
Section 202, for example, does not contain "new tax regime". The prefix gives the
embedding and BM25 that context. Both search methods see it; the LLM gets the plain
text (each excerpt it sees already has the section titles in its header line).
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
        return {**self.inner.config(), "search_prefix": "section header (dense + bm25)"}

    def chunk(self, doc: Document) -> list[Chunk]:
        out = []
        for c in self.inner.chunk(doc):
            number = c.chunk_id.rsplit(":", 1)[1]
            prefix = section_header(c.sections, c.section_titles)
            out.append(
                replace(
                    c,
                    chunk_id=f"{self.name}:{number}",
                    extra={**c.extra, "search_prefix": prefix + "\n" if prefix else ""},
                )
            )
        return out
