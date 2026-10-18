# Income Tax Agent

Ask questions about India's **Income-tax Act, 2025** (as amended by Finance Act, 2026) in
plain English. The app finds the relevant sections and answers **only** from them, with
citations like `[Section 202]`. If the Act doesn't cover the question, it says so.

> Not tax advice. Questions are sent to Google's Gemini API, so don't type personal details.

## How it works

1. **Ingest.** The 674-page PDF is turned into clean text. Page headers, footers and
   amendment footnotes are removed, because the footnotes often quote old, repealed law.
2. **Index.** The text is split into 1,000-character chunks. Each chunk is tagged with its
   section number and embedded locally with `bge-base` (fastembed). The vectors are stored in Chroma.
3. **Expand the query.** Gemini Flash-Lite rewrites the question into 3 extra search queries
   in the Act's own wording: "12 lakh" becomes "Rs. 1200000", "TDS" becomes "tax deducted at
   source", and one query is written like a sentence of the Act. The original question is
   always searched too, and the lists are merged with Reciprocal Rank Fusion.
4. **Retrieve.** Search is dense, BM25 or hybrid. Each hit also brings its neighbouring chunks
   from the same section.
5. **Answer.** A LangGraph pipeline sends the retrieved text to Gemini, which answers with citations.

## Results

Every design choice is measured on 26 questions written from the Act's text. All runs and
their configs are in [eval/results](eval/results/README.md).

| Setup | Right section first | Right section in top 5 | MRR |
|---|---|---|---|
| Baseline: plain chunks, dense search | 13/22 | 18/22 | 0.69 |
| Section title added to each chunk, dense + neighbours | 15/22 | 20/22 | 0.76 |
| + LLM query expansion (used by the app) | 18/22 | 21/22 | 0.87 |

Answers, graded by a second Gemini model (first 18 questions):
**15/18** correct or partly correct, and **17/18** faithful to the retrieved text.

## Run it

```bash
uv sync
cp .env.example .env    # add GOOGLE_API_KEY and the Gemini model names
uv run streamlit run app/streamlit_app.py
```

The app's index is in the repo, so you don't need the PDF to run it.
You can also ask from the command line: `uv run python scripts/ask.py "What is the standard deduction?"`

## Rebuild from the PDF

Put the Act PDF in `data/raw/`. It is 118 MB, too big for Git. Then:

```bash
uv run python -m income_tax_agent.ingest.extract   # PDF -> pages.jsonl (~3 min, once)
uv run python -m income_tax_agent.index --header   # chunk, embed, write data/index/<name>/
```

## Evaluate

```bash
uv run python eval/run_eval.py --modes dense bm25 hybrid   # retrieval metrics, no LLM
uv run python eval/run_eval.py --expand --neighbours        # same, with LLM query expansion
uv run python eval/run_eval.py --judge                     # answers + LLM judge
uv run python eval/compare.py diff <run> <run>             # what changed between two runs
```

## Tests

```bash
uv run pytest
```

CI runs them with fake embeddings and a fake LLM, so it needs no keys or downloads.
