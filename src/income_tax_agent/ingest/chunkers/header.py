"""Wrap another chunker: same chunks, plus a "Section N: <title>" line for search.

A chunk from the middle of a section often never names it. The slab-table chunk of
Section 202, for example, does not contain "new tax regime". The prefix gives the
embedding and BM25 that context. Both search methods see it; the LLM gets the plain
text (each excerpt it sees already has the section titles in its header line).

With `breadcrumb`, the line starts with the section's chapter and part, because some
titles only make sense under them:
"Chapter XIII: Determination of tax in special cases > E. Special provisions relating to
non-residents and foreign companies > Section 214: Tax on investment income and ...".
"""

from dataclasses import dataclass, replace

from income_tax_agent.ingest.chunkers.base import Chunk, Chunker
from income_tax_agent.ingest.sections import Document


def section_header(numbers: list[str], titles: list[str], paths: list[list[str]] | None = None) -> str:
    """"Section 202: New tax regime ...", one line per section ("Schedule XV: ..." as is).

    `paths`: each section's headings (SectionStart.path), put in front of its line.
    """
    lines = []
    for i, (number, title) in enumerate(zip(numbers, titles)):
        label = number if number.startswith("Schedule") else f"Section {number}"
        line = f"{label}: {title}" if title else label
        lines.append(" > ".join([*(paths[i] if paths else []), line]))
    return "\n".join(lines)


@dataclass
class HeaderPrefixChunker:
    inner: Chunker
    breadcrumb: bool = False

    @property
    def name(self) -> str:
        return f"{self.inner.name}-{'breadcrumb' if self.breadcrumb else 'header'}"

    def config(self) -> dict:
        what = "chapter > part > section header" if self.breadcrumb else "section header"
        return {**self.inner.config(), "search_prefix": f"{what} (dense + bm25)"}

    def chunk(self, doc: Document) -> list[Chunk]:
        paths = {s.number: s.path for s in doc.sections}
        out = []
        for c in self.inner.chunk(doc):
            number = c.chunk_id.rsplit(":", 1)[1]
            chunk_paths = [paths.get(n, []) for n in c.sections] if self.breadcrumb else None
            prefix = section_header(c.sections, c.section_titles, chunk_paths)
            out.append(
                replace(
                    c,
                    chunk_id=f"{self.name}:{number}",
                    extra={**c.extra, "search_prefix": prefix + "\n" if prefix else ""},
                )
            )
        return out
