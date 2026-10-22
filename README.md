# Income Tax Agent

Ask questions about India's **Income-tax Act, 2025** (as amended by Finance Act, 2026) in
plain English. The app finds the relevant sections and answers **only** from them, with
citations like `[Section 202]`. If the Act doesn't cover the question, it says so.

**Live demo:** https://income-tax-agent-wd2i88cfs4nwgtvcglq7cf.streamlit.app/

> Not tax advice. Questions are sent to Google's Gemini API, so don't type personal details.

## How it works

1. **Ingest.** The 674-page PDF is turned into clean text. Page headers, footers and
   amendment footnotes are removed, because the footnotes often quote old, repealed law.
2. **Index.** The text is split into 1,000-character chunks. Each chunk is tagged with its
   section number and embedded locally with `bge-base` (fastembed). The vectors are stored in Chroma.
3. **Expand the query.** Gemini Flash-Lite rewrites the question into 3 extra search queries
   in the Act's own wording: "12 lakh" becomes "Rs. 1200000", "TDS" becomes "tax deducted at
   source", and one query is written like a sentence of the Act. The original question is
   always searched too. The lists are merged by each chunk's *best* rank in any list, so a
   section that only one query finds at the top is not outvoted by chunks every query finds
   halfway down.
4. **Retrieve.** Search is hybrid: dense (meaning) and BM25 (exact words), merged with
   Reciprocal Rank Fusion using a small k, so a strong hit from either one counts. Each hit
   also brings its neighbouring chunks from the same section.
5. **Answer.** A LangGraph pipeline sends the retrieved text to Gemini, which answers with citations.

## Results

Every design choice is measured on 26 questions written from the Act's text, plus 10
held-out questions. The key runs are in [eval/results](eval/results/README.md), and every
run with its config is in [all_runs.md](eval/results/all_runs.md).

| Setup | Right section first | Right section in top 5 | MRR |
|---|---|---|---|
| Baseline: plain chunks, dense search | 13/22 | 18/22 | 0.69 |
| Section title added to each chunk, dense + neighbours | 15/22 | 20/22 | 0.76 |
| + LLM query expansion | 18/22 | 21/22 | 0.87 |
| Hybrid + expansion, best-rank merge (used by the app) | 18/22 | 21/22 | 0.88 |
| Same, on 10 held-out questions | 8/10 | 10/10 | 0.88 |
| Experiment: structured chunks, app setup | 18/22 | 22/22 | 0.89 |
| Same, on 10 held-out questions | 8/10 | 10/10 | 0.86 |

The held-out questions were written after the expansion prompt was frozen, to check it
was not tuned to the first 22. Without expansion, hybrid scores 0.78 MRR on them.

**Structured chunks (experiment).** Instead of cutting every 1,000 characters, this chunker
cuts where the Act does: never across sections, then at sub-sections, one chunk per
definition, and table rows with the column headings repeated. Definitions improved a lot
("senior citizen" went from not found to rank 1 with dense search). But short definition
chunks sometimes beat the right answer on general questions. Overall, retrieval is about
the same. The answer eval will decide if it replaces the app's index.

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
uv run python -m income_tax_agent.index --chunker structured   # the structured-chunk index
```

The app's sidebar has an index picker, so you can compare the default fixed chunks with the
structured chunks on the same question. Both indexes are in the repo.

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
