# Income Tax Agent

Ask questions about India's **Income-tax Act, 2025** (as amended by Finance Act, 2026) in
plain English. The app finds the relevant sections and answers **only** from them, with
citations like `[Section 202]`. If the Act doesn't cover the question, it says so.

**Live demo:** https://income-tax-agent-wd2i88cfs4nwgtvcglq7cf.streamlit.app/

> Not tax advice. Questions are sent to Google's Gemini API, so don't type personal details.

## How it works

1. **Ingest.** The 674-page PDF is turned into clean text. Page headers, footers and
   amendment footnotes are removed, because the footnotes often quote old, repealed law.
   With them kept, 2 of 6 test answers stated the repealed law as current (see
   "Removing amendment footnotes" under Results).
2. **Index.** The text is split where the Act is split: never across sections, then at
   sub-sections, one chunk per definition, and table rows with the column headings repeated.
   Each chunk is tagged with its section number and embedded locally with `bge-base`
   (fastembed). The vectors are stored in Chroma.
3. **Resolve follow-ups.** If the chat has earlier turns, Gemini Flash-Lite turns the new
   question into one that stands on its own. After a question about the health insurance
   deduction, "And for senior citizens?" becomes a question about the health insurance
   deduction for senior citizens. The first question of a chat skips this step.
4. **Expand the query.** Gemini Flash-Lite rewrites the question into 3 extra search queries
   in the Act's own wording: "12 lakh" becomes "Rs. 1200000", "TDS" becomes "tax deducted at
   source", and one query is written like a sentence of the Act. The original question is
   always searched too.
5. **Retrieve.** Each query takes its top 10 chunks by dense (meaning) search.
6. **Rerank.** A small local cross-encoder (`ms-marco-MiniLM-L-6`, 80 MB) reads the question
   next to each pooled chunk and orders them (see "Reranker scoring" below). The top 5 go
   on, each with its neighbouring chunks from the same section.
7. **Answer.** A LangGraph pipeline sends the retrieved text to Gemini, which answers with
   citations. The prompt warns that some excerpts may be off-topic, so one bad excerpt at
   the top does not make it refuse.

**Chat memory.** The steps above run as a LangGraph graph. LangGraph's checkpointer saves
each chat between questions, so the app remembers what you asked before. Each browser
session gets its own chat, so visitors never see each other's questions.

- Only the past questions and answers are kept. Everything else starts fresh for each new
  question.
- How a follow-up works: step 3 sends Gemini the last 3 questions and answers (each answer
  cut to its first 600 characters, enough to know what "it" or "that" means) plus the new
  question. Gemini replies with the new question written out in full. That full question is
  what gets searched and answered.
- The answer step never sees the past turns, so every answer comes from the Act, not from
  an earlier answer.
- If step 3 fails, the question is used as typed.
- Chats are kept in memory only: reloading the page starts a new chat. That is enough for a
  demo; a database would keep chats for longer.

**Reranker scoring.** Dense search is fast but rough: the question and each chunk are turned
into vectors separately and never read together. The reranker is slower but more accurate:
it reads the question and one chunk together and gives a score for how well the chunk
answers it (higher is better). It only scores the ~35 chunks that the 4 searches found.

- The question is scored against each chunk, and so is each of the 3 rewrites.
- A chunk's final score = its score against the question + **half** of its best score against
  any rewrite.
- Why both: the question keeps the user's key words ("non-resident *Indian*"), and the
  rewrites bring the Act's wording ("Rs. 200000"). Either one alone lost a question in the eval.
- Why the best rewrite, not the average: usually only one of the three matches the Act's
  wording, and an average would water it down.
- Why half: the question counts twice as much, so a rewrite can lift a chunk but not take
  over. 0.5 is the only value tried; tuning it on 26 questions would risk overfitting.

Example, "Can I accept 3 lakh in cash when I sell my car?" The answer is Section 186 (no cash
receipts of Rs. 2 lakh or more). One rewrite reads like the Act: "No person shall receive an
amount of Rs. 200000 or more in cash in relation to transfer of any asset".

| Chunk | vs question | Best rewrite | Final score |
|---|---|---|---|
| Section 186 (right) | -11.03 | +5.75 | -11.03 + 0.5 × 5.75 = **-8.15** |
| Section 70 (wrong) | -8.53 | -2.73 | -8.53 + 0.5 × -2.73 = **-9.89** |

By the question alone, Section 186 ranks 9th: "3 lakh" and "car" share no words with the Act's
"Rs. 200000" and "transfer of any asset". With the rewrite's score added, it ranks first.

## Results

Every design choice is measured on 30 dev questions written from the Act's text (26 it
should answer, 4 it should refuse), plus 10 held-out questions. The full config, per-question
ranks and the alternatives that lost are in [eval/results](eval/results/README.md).

**hit@1** = the right section is the first result; **hit@5** = it is in the top 5;
**MRR** = the mean of 1/rank of the first right result (1.00 = always first). Counts are
questions: on held-out, one question is 10 points.

**A. Fixed 1,000-character chunks (how the app started).** Each step run with the settings it had then.

| # | What changed | Search | Query expansion | Reranker | Neighbours | Dev hit@1 | Dev hit@5 | Dev MRR | Held-out hit@1 | Held-out hit@5 | Held-out MRR |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 | Baseline | dense | – | – | – | 14/26 | 20/26 | 0.64 | 2/10 | 6/10 | 0.36 |
| A2 | + section title in each chunk | dense | – | – | – | 16/26 | 22/26 | 0.70 | 5/10 | 8/10 | 0.62 |
| A3 | + query expansion, + neighbours | dense | ✓ | – | ✓ | 20/26 | 24/26 | 0.83 | 8/10 | 9/10 | 0.83 |
| A4 | + hybrid search (dense + BM25) | hybrid | ✓ | – | ✓ | 19/26 | 24/26 | 0.83 | 8/10 | 10/10 | 0.88 |

**B. Structured chunks, one technique at a time (the app).** Today's settings, in the order the pipeline runs them.

| # | What changed | Search | Query expansion | Reranker | Neighbours | Dev hit@1 | Dev hit@5 | Dev MRR | Held-out hit@1 | Held-out hit@5 | Held-out MRR |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | Structured chunks, dense search only | dense | – | – | – | 16/26 | 24/26 | 0.74 | 6/10 | 9/10 | 0.72 |
| B2 | + query expansion | dense | ✓ | – | – | 20/26 | 25/26 | 0.85 | 8/10 | 10/10 | 0.85 |
| B3 | + reranker, scored against the question | dense | ✓ | question | – | 22/26 | 25/26 | 0.90 | 8/10 | 9/10 | 0.84 |
| B4 | + reranker also scores the rewrites | dense | ✓ | question + half of best rewrite | – | 24/26 | 26/26 | 0.96 | 9/10 | 10/10 | 0.93 |
| **B5** | **+ neighbour chunks (the app)** | dense | ✓ | question + half of best rewrite | ✓ | **24/26** | **26/26** | **0.96** | **9/10** | **10/10** | **0.93** |
| ↳ | B5 with hybrid search, for comparison | hybrid | ✓ | question + half of best rewrite | ✓ | 23/26 | 26/26 | 0.94 | 8/10 | 10/10 | 0.88 |

- **Query expansion:** Gemini writes 3 extra search queries in the Act's wording; the
  question is searched too. Without a reranker, their result lists are merged (RRF in A3,
  best rank from A4 on).
- **Reranker:** "question + half of best rewrite" means a chunk's score against the question,
  plus half its best score against any of the rewrites.
- **Neighbours:** the chunks before and after each hit, from the same section. On
  structured chunks they can't change these numbers (a neighbour is always the same
  section); they give the answer model the rest of a sub-section or table.

What the numbers show:

- **Query expansion is the biggest single gain:** +4 dev and +2 held-out questions ranked
  first (B1 → B2).
- **The reranker needs the rewrites.** Scored against the question alone it adds +2 dev and
  nothing on held-out. Adding the rewrite scores adds +2 dev and +1 held-out (see the cash
  example under "Reranker scoring").
- **Structured chunks alone** rank as many questions first as fixed chunks with titles
  (16/26), but find more in the top 5 (24 vs 22) and do better on held-out (6 vs 5).
- **Dense beats hybrid** by one question on each set once the reranker is on, so the app uses dense.

The held-out questions were written after the expansion prompt was frozen, to check it
was not tuned to the dev questions. The reranker's scoring rule was chosen partly on a
held-out question, so its held-out score is a little optimistic.

**Reranker models.** A grid of 4 indexes x 3 search modes x expansion on/off x reranker
on/off (96 runs, on the 23-question dev set of the time) picked the app's setup. Then the
reranker model was swapped, keeping everything else the same: structured chunks, hybrid
search + query expansion + neighbours, 20 candidates per query, scored against the question
only (the rewrite scores came later).

| Reranker | Size | Dev hit@1 | Dev hit@5 | Dev MRR | Held-out hit@1 | Held-out hit@5 | Held-out MRR |
|---|---|---|---|---|---|---|---|
| **`ms-marco-MiniLM-L-6-v2` (chosen)** | 80 MB | **20/23** | **23/23** | **0.93** | **8/10** | 9/10 | **0.83** |
| `ms-marco-MiniLM-L-12-v2` | 120 MB | 16/23 | 23/23 | 0.85 | 8/10 | 9/10 | 0.83 |
| `jina-reranker-v1-turbo-en` | 150 MB | 16/23 | 21/23 | 0.80 | 6/10 | 9/10 | 0.72 |
| `bge-reranker-base` | 1 GB | 19/23 | 23/23 | 0.90 | 4/10 | 10/10 | 0.64 |

The smallest model was the best or tied on every number except held-out hit@5, where
`bge-reranker-base` found one more question in the top 5. Bigger was not better: `bge-reranker-base`
is 12x the size and 8x slower, and ranked only 4 of 10 held-out questions first. So the app
uses MiniLM-L-6, which adds about 2 seconds per question on a laptop CPU. A second jina model
was also tried, but its run was not saved. The app has a sidebar switch to compare answers
with and without the reranker.

**Structured vs fixed chunks with the full app setup.** In the same grid, structured chunks
ranked 32 of 33 dev and held-out questions first, fixed chunks 26, probably because a whole
sub-section is a cleaner unit for the reranker to judge.

**Tried and rejected: chapter headings on chunks.** Adding "Chapter XIII > Part E: Special
provisions relating to non-residents > Section 214" to each chunk's search text helped vague
section titles, but blurred neighbouring sections: every section in Part C "New tax regime"
then matched "new tax regime", and the slab-rate question dropped from rank 3 to 10.

**Removing amendment footnotes.** The PDF has 163 amendment footnotes, and 81 of them quote
the old, repealed wording. For example: "Prior to its substitution, section 446 read as under:
... a penalty of 0.5% of turnover". To test whether removing them matters, 6 trap questions
were written ([eval/traps.jsonl](eval/traps.jsonl)). Each one is tied to a footnote whose old
text gives a different answer from today's law. Same setup on both sides: fixed 1,000-character
chunks, dense search only.

| | Answers stating repealed law | Correct | Dev hit@5 | Held-out hit@5 |
|---|---|---|---|---|
| Footnotes kept | **2/6** | 3/6 | 18/26 | 7/10 |
| Footnotes removed | **0/6** | 2/6 | 20/26 | 6/10 |

- **Retrieval scores can't see the harm.** They move by a question or two either way. The
  answers show it: with footnotes kept, the app said a missed audit costs "0.5% of turnover"
  (repealed; today it is a fee of Rs 75,000, then Rs 1,50,000).
- **Kept footnotes also break citations.** A footnote line like `295. Sub. by ...` looks like the
  start of Section 295, so many chunks get the wrong section number, and the answers cite it.
- "Correct" uses two grades corrected by hand. On the footnotes-removed side, most misses were
  refusals: plain dense search did not find the section.
- Six questions is small, but the two failures are clear. Full write-up:
  [eval/experiments/footnotes](eval/experiments/footnotes/README.md).

Answers, graded by a second Gemini model (first answer eval, older app setup, 18 questions):
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
uv run python eval/run_eval.py --judge --questions eval/traps.jsonl   # + "states old law" rate
uv run python eval/check_questions.py --questions eval/traps.jsonl    # traps tied to old-text footnotes
uv run python eval/compare.py diff <run> <run>             # what changed between two runs
```

`--judge-model` and `--judge-thinking` (minimal to high) change the judge for one run.
Results are saved per run; the key runs are listed in [eval/results](eval/results/README.md).
Experiments that need their own explanation have a write-up in [eval/experiments](eval/experiments/).

## Tests

```bash
uv run pytest
```

CI runs them with fake embeddings and a fake LLM, so it needs no keys or downloads.
