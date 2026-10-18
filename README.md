# Income Tax Agent

Ask questions about India's **Income-tax Act, 2025** (as amended by Finance Act, 2026) in
plain English. Answers come only from the Act's text, with section citations.

Status: ingestion done (Phase 1). Retrieval, eval and the app are next.

## Setup

```bash
uv sync
cp .env.example .env   # then fill in GOOGLE_API_KEY and the Gemini model names
```

Put the Act PDF in `data/raw/` (it is 118 MB, so it is not in Git).

## Ingestion

```bash
uv run python -m income_tax_agent.ingest.extract   # PDF -> data/processed/pages.jsonl (~3 min, run once)
uv run python -m income_tax_agent.ingest.clean     # clean + detect sections, saves removed footnotes
```

Cleaning removes page headers/footers, and the 163 amendment footnotes (81 of them quote
old, repealed wording that could otherwise leak into answers).

## Tests

```bash
uv run pytest
```
