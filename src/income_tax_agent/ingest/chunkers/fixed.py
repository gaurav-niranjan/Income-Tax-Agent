"""Baseline chunker: fixed-size character windows with overlap.

It knows nothing about the Act's structure, which is the point: it is the baseline the
structured chunker must beat. The only nicety is that cuts snap to a line break or space,
so words are not split in half.
"""

from dataclasses import dataclass

from income_tax_agent.ingest.chunkers.base import Chunk
from income_tax_agent.ingest.sections import Document


@dataclass
class FixedSizeChunker:
    size: int = 1000
    overlap: int = 150

    @property
    def name(self) -> str:
        return f"fixed-{self.size}-{self.overlap}"

    def config(self) -> dict:
        return {"type": "fixed", "size": self.size, "overlap": self.overlap}

    def _snap_end(self, text: str, start: int) -> int:
        """End of the window starting at `start`, moved back to a line break or space."""
        end = start + self.size
        if end >= len(text):
            return len(text)
        # Only look back over the last 20% of the window, so chunks stay near full size.
        floor = start + int(self.size * 0.8)
        for sep in ("\n", " "):
            cut = text.rfind(sep, floor, end)
            if cut != -1:
                return cut + 1  # Keep the separator in this chunk.
        return end

    def _snap_start(self, text: str, start: int) -> int:
        """Move a start position forward to the beginning of a word."""
        while 0 < start < len(text) and not text[start - 1].isspace():
            start += 1
        return start

    def chunk(self, doc: Document) -> list[Chunk]:
        text = doc.text
        chunks: list[Chunk] = []
        start = 0
        while start < len(text):
            end = self._snap_end(text, start)
            body = text[start:end].strip()
            if body:
                # Non-space characters per section. The eval uses this for a "strict" hit:
                # a chunk only counts for a section that makes up a real share of it.
                section_chars = doc.section_chars_between(start, end)
                sections = [s for s in doc.sections_between(start, end) if s.number in section_chars]
                chunks.append(
                    Chunk(
                        chunk_id=f"{self.name}:{len(chunks):06d}",
                        text=body,
                        pages=doc.pages_between(start, end),
                        sections=[s.number for s in sections],
                        section_titles=[s.title for s in sections],
                        extra={"start": start, "end": end, "section_chars": section_chars},
                    )
                )
            if end >= len(text):
                break
            # Step back by the overlap, but always move forward.
            start = max(self._snap_start(text, end - self.overlap), start + 1)
        return chunks
