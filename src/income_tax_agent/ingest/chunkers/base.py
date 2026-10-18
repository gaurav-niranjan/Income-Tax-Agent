"""What every chunker produces, and the interface it implements."""

from dataclasses import asdict, dataclass, field
from typing import Protocol

from income_tax_agent.ingest.sections import Document


@dataclass
class Chunk:
    chunk_id: str  # stable, e.g. "fixed-1000-150:000123"
    text: str  # what gets embedded and searched
    pages: list[int]  # PDF page numbers covered
    sections: list[str]  # section numbers covered, e.g. ["202"] or ["93", "94"]
    section_titles: list[str]
    extra: dict = field(default_factory=dict)  # chunker-specific details

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Chunk":
        return cls(**d)


class Chunker(Protocol):
    @property
    def name(self) -> str:
        """Short config name, used in the index folder name, e.g. "fixed-1000-150"."""
        ...

    def chunk(self, doc: Document) -> list[Chunk]: ...

    def config(self) -> dict:
        """Every setting that affects the output. Saved in the index manifest."""
        ...
