# Income Tax Agent

Ask questions about India's **Income-tax Act, 2025** (as amended by Finance Act, 2026) in
plain English. The app finds the relevant sections and answers **only** from them, with
citations like `[Section 202]`. If the Act doesn't cover the question, it says so.

**Live demo:** https://income-tax-agent-wd2i88cfs4nwgtvcglq7cf.streamlit.app/

> Not tax advice. Questions are sent to Google's Gemini API, so don't type personal details.

## How it works

1. **Ingest.** The 674-page PDF is turned into clean text. Page headers, footers and
   amendment footnotes are removed, because the footnotes often quote old, repealed law.
2. **Index.** The text is split where the Act is split: never across sections, then at
   sub-sections, one chunk per definition, and table rows with the column headings repeated.
   Each chunk is tagged with its section number and embedded locally with `bge-base`
   (fastembed). The vectors are stored in Chroma.
3. **Expand the query.** Gemini Flash-Lite rewrites the question into 3 extra search queries
   in the Act's own wording: "12 lakh" becomes "Rs. 1200000", "TDS" becomes "tax deducted at
   source", and one query is written like a sentence of the Act. The original question is
   always searched too.
4. **Retrieve.** Each query takes its top 10 chunks by dense (meaning) search.
5. **Rerank.** A small local cross-encoder (`ms-marco-MiniLM-L-6`, 80 MB) reads the question
   next to each pooled chunk and orders them. A chunk's score is its score against the
   question plus half its best score against a rewrite: the question keeps the user's key
   words ("non-resident *Indian*"), the rewrites bring the Act's wording ("two lakh rupees").
   The top 5 go on, each with its neighbouring chunks from the same section.
6. **Answer.** A LangGraph pipeline sends the retrieved text to Gemini, which answers with
   citations. The prompt warns that some excerpts may be off-topic, so one bad excerpt at
   the top does not make it refuse.

## Results

Every design choice is measured on 27 questions written from the Act's text, plus 10
held-out questions. Each step, and the alternatives that lost, are in
[eval/results](eval/results/README.md), with the full config and per-question ranks of every run.

| Setup | Right section first | Right section in top 5 | MRR |
|---|---|---|---|
| Baseline: plain chunks, dense search | 13/22 | 18/22 | 0.69 |
| Section title added to each chunk, dense + neighbours | 15/22 | 20/22 | 0.76 |
| + LLM query expansion | 18/22 | 21/22 | 0.87 |
| Hybrid + expansion, best-rank merge | 18/22 | 21/22 | 0.88 |
| Structured chunks, same setup (23 questions, NRI question added) | 18/23 | 22/23 | 0.86 |
| **+ reranker, dense search (used by the app)** | **23/23** | **23/23** | **1.00** |
| Same, on 10 held-out questions | 9/10 | 10/10 | 0.93 |

The held-out questions were written after the expansion prompt was frozen, to check it
was not tuned to the first 22. The reranker's scoring rule was chosen partly on a held-out
question, so its held-out score is a little optimistic.

**Reranker.** A grid of 4 indexes x 3 search modes x expansion on/off x reranker on/off
(96 runs) picked the app's setup. The reranker was the biggest single gain (+4 to +5
questions ranked first). With it, the first-stage search mode barely matters, since it only
has to get the right chunk into the pool. Of 5 rerankers tried, the smallest was best; the
1 GB `bge-reranker-base` was not better. It adds about 2 seconds per question on a laptop
CPU. The app has a sidebar switch to compare answers with and without it.

**Structured chunks.** They beat fixed 1,000-character chunks once the reranker is on (32
vs 26 of 33 questions ranked first), probably because a whole sub-section is a cleaner unit
for the reranker to judge.

**Tried and rejected: chapter headings on chunks.** Adding "Chapter XIII > Part E: Special
provisions relating to non-residents > Section 214" to each chunk's search text helped vague
section titles, but blurred neighbouring sections: every section in Part C "New tax regime"
then matched "new tax regime", and the slab-rate question dropped from rank 3 to 10.

Answers, graded by a second Gemini model (first 18 questions):
**15/18** correct or partly correct, and **17/18** faithful to the retrieved text.

## Run it

```bash
uv sync
cp .env.example .env    # add GOOGLE_API_KEY and the Gemini model names
uv run streamlit run app/streamlit_app.py
```

The app's index is in the repo, so you don't need the PDF to run it. The first start
downloads the embedding model (~210 MB) and the reranker (~80 MB).
You can also ask from the command line: `uv run python scripts/ask.py "What is the standard deduction?"`

## Rebuild from the PDF

Put the Act PDF in `data/raw/`. It is 118 MB, too big for Git. Then:

```bash
uv run python -m income_tax_agent.ingest.extract   # PDF -> pages.jsonl (~3 min, once)
uv run python -m income_tax_agent.index --chunker structured   # the app's index
uv run python -m income_tax_agent.index --header   # fixed 1,000-character chunks + section titles
```

The app's sidebar has an index picker, so you can compare the default structured chunks
with the fixed chunks on the same question. Both indexes are in the repo.

## Evaluate

```bash
uv run python eval/run_eval.py --modes dense bm25 hybrid   # retrieval metrics, no LLM
uv run python eval/run_eval.py --expand --neighbours        # same, with LLM query expansion
uv run python eval/run_eval.py --modes dense --expand --neighbours --rerank   # the app's setup
uv run python eval/run_eval.py --judge                     # answers + LLM judge
uv run python eval/compare.py diff <run> <run>             # what changed between two runs
```

## Tests

```bash
uv run pytest
```

CI runs them with fake embeddings and a fake LLM, so it needs no keys or downloads.
