"""Sanity-check the eval set against the Act's text. Does not run retrieval.

For every in-scope question:
- each expected section exists,
- each phrase appears in one of the expected sections (so the reference is checkable),
- each phrase fits inside at least one chunk of the index (so a phrase-hit is possible).

Run: uv run python eval/check_questions.py [--index fixed-1000-150__bge-base]
"""

import argparse
import json
from pathlib import Path

from metrics import load_questions, normalize

from income_tax_agent.config import get_settings
from income_tax_agent.ingest.clean import clean_pages
from income_tax_agent.ingest.extract import load_pages
from income_tax_agent.ingest.sections import build_document


def main() -> None:
    settings = get_settings()
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default=settings.index_name)
    parser.add_argument("--questions", type=Path, default=Path(__file__).parent / "questions.jsonl")
    args = parser.parse_args()

    doc = build_document(clean_pages(load_pages(settings.pages_path), settings.strip_footnotes).pages)
    ends = [s.offset for s in doc.sections[1:]] + [len(doc.text)]
    section_text = {s.number: normalize(doc.text[s.offset : e]) for s, e in zip(doc.sections, ends)}
    with (settings.index_dir / args.index / "chunks.jsonl").open() as f:
        chunk_texts = [normalize(json.loads(line)["text"]) for line in f]

    problems = 0
    for q in load_questions(args.questions):
        if not q.in_scope:
            continue
        for s in q.sections:
            if s not in section_text:
                print(f"{q.id}: section {s} does not exist")
                problems += 1
        for p in q.phrases:
            where = [s for s in q.sections if normalize(p) in section_text.get(s, "")]
            n_chunks = sum(normalize(p) in t for t in chunk_texts)
            status = "ok" if where and n_chunks else "PROBLEM"
            problems += status != "ok"
            print(f"{q.id}: {status:<7} in sections {where or '-'}, in {n_chunks} chunks: {p!r}")
    print(f"\n{problems} problem(s)")


if __name__ == "__main__":
    main()
