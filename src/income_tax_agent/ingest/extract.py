"""Extract text from the PDF once and cache it to `data/processed/pages.jsonl`.

We store the *raw* layout text. Cleaning happens later, so changing the cleaner
never needs a slow re-extraction.

Run: uv run python -m income_tax_agent.ingest.extract
"""

import json
from collections.abc import Iterator
from pathlib import Path

import pdfplumber

from income_tax_agent.config import get_settings


def extract_pages(pdf_path: Path) -> Iterator[dict]:
    """Yield {"page": n, "text": ...} for each page, 1-based page numbers."""
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            # layout=True keeps each table row on one line (the tables have no borders).
            text = page.extract_text(layout=True) or ""
            # Layout mode pads every line with spaces to the page width. Trim the right side
            # only: the left indent tells us how deeply a clause is nested.
            text = "\n".join(line.rstrip() for line in text.splitlines())
            yield {"page": i, "text": text}
            # Free the parsed page objects; otherwise memory grows over 674 pages.
            page.flush_cache()


def write_pages_cache(pdf_path: Path, out_path: Path) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with out_path.open("w", encoding="utf-8") as f:
        for record in extract_pages(pdf_path):
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
            if count % 50 == 0:
                print(f"  extracted {count} pages")
    return count


def load_pages(path: Path | None = None) -> list[dict]:
    path = path or get_settings().pages_path
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def main() -> None:
    s = get_settings()
    n = write_pages_cache(s.pdf_path, s.pages_path)
    print(f"Wrote {n} pages to {s.pages_path}")


if __name__ == "__main__":
    main()
