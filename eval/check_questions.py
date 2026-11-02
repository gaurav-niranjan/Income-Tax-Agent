"""Sanity-check the eval set against the Act's text. Does not run retrieval.

For every in-scope question:
- each expected section exists,
- each phrase appears in one of the expected sections (so the reference is checkable),
- each phrase fits inside at least one chunk of the index (so a phrase-hit is possible).

For trap questions (traps.jsonl, `extra.footnote`): the footnote exists, quotes old text, and the
question's old-law regex matches it but not the current-law reference.

Run: uv run python eval/check_questions.py [--index fixed-1000-150__bge-base] [--questions eval/traps.jsonl]
"""

import argparse
import json
from pathlib import Path

from judge import uses_old_law
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
    # Written by clean.py. Footnote numbers restart in each printout, so the key includes the page.
    with (settings.pages_path.parent / "footnotes_removed.jsonl").open() as f:
        footnotes = {(r["number"], r["page"]): r for r in map(json.loads, f)}

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
        if "footnote" in q.extra:
            problems += not check_trap(q, footnotes)
    print(f"\n{problems} problem(s)")


def check_trap(q, footnotes: dict) -> bool:
    """A trap question (traps.jsonl) is only fair if its footnote really quotes old text that the
    old-law check catches, and the current-law reference does not trip that check."""
    fn = q.extra["footnote"]
    f = footnotes.get((fn["number"], fn["page"]))
    checks = {
        "footnote found": f is not None,
        "quotes old text": bool(f and f["quotes_old_text"]),
        "old_law matches footnote": bool(f and uses_old_law(f["text"], q.extra["old_law"])),
        "reference clean": not uses_old_law(q.reference, q.extra["old_law"]),
    }
    ok = all(checks.values())
    failed = [name for name, passed in checks.items() if not passed]
    print(f"{q.id}: {'ok' if ok else 'PROBLEM':<7} footnote {fn['number']} p.{fn['page']}"
          + (f" failed: {', '.join(failed)}" if failed else ""))
    return ok


if __name__ == "__main__":
    main()
