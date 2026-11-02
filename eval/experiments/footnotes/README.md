# Experiment: removing amendment footnotes

**Question.** The Act's PDF has about 163 amendment footnotes. 81 of them quote the *old, repealed*
wording, for example "Prior to its substitution, section 446 read as under: ... a penalty of 0.5% of
turnover". Cleaning removes them (`STRIP_FOOTNOTES=true`, [clean.py](../../../src/income_tax_agent/ingest/clean.py)).
Does that matter?

**Answer.** Yes. With footnotes kept, **2 of 6** trap answers stated repealed law as if it were
current. With footnotes removed, **0 of 6** did.

Run on 2026-11-02. All runs are listed in [eval/results/README.md](../../results/README.md)
("Footnotes ablation" rows).

## Setup

Both sides are the same, except for the cleaning flag.

| | |
|---|---|
| Chunks | fixed, 1,000 characters, 150 overlap (`fixed-1000-150__bge-base`) |
| Embeddings | `BAAI/bge-base-en-v1.5` |
| Search | dense only: no query expansion, no reranker, no neighbours (the A1 baseline) |
| Answer model | Gemini 3.5 Flash-Lite, minimal thinking, top 5 chunks |
| Judge | Gemini 3.5 Flash-Lite, high thinking (the usual judge, Flash, had no quota) |
| Footnotes kept | 2,193 chunks, 1.74M characters |
| Footnotes removed | 2,120 chunks, 1.68M characters |

## Answers: kept footnotes give old law

Six trap questions, [eval/traps.jsonl](../../traps.jsonl). **Every question is tied to one footnote
that quotes old text and gives a different answer to that same question.** Each question lists regexes
for the old figure (`extra.old_law`). An answer that matches one of them "states old law". This is a
text check, so no judge is needed.

| ID | Question (short) | Current law | Old text in the footnote | Footnote: where its marker sits |
|---|---|---|---|---|
| t01 | TCS (tax collected at source) on a Rs 12 lakh overseas tour package | 2%, no threshold (S.394(1), Sl. 8) | 5% up to Rs 10 lakh, 20% above | 89 (p.472): `89[2%]` in the tour package row |
| t02 | Deduct loan interest from dividend income? | No deduction (S.93(2)) | Up to 20% of the dividends | 10c (p.127): all of S.93(2) |
| t03 | Accounts not audited | Fee Rs 75,000, then Rs 1,50,000 (S.428(c)) | Penalty 0.5% of turnover or Rs 1.5 lakh | 10 (p.532): all of S.446, which used to be this penalty |
| t04 | Late statement of financial transaction | Rs 200 a day, max Rs 1 lakh (S.427(3)) | Rs 500 a day | 12 (p.540): all of S.454, which used to be this penalty |
| t05 | Evading over Rs 60 lakh of tax | Simple imprisonment up to 2 years, or fine, or both (S.478) | Rigorous imprisonment, 6 months to 7 years | 24 (p.564): S.478(1) and (2) |
| t06 | TDS on Motor Accidents Tribunal interest to an individual | No TDS, any amount (S.393(4)) | No TDS only up to Rs 50,000 | 83 (p.470): S.393(4) Table, Sl. 7, item (iv) |

How the link is checked:

- **By hand:** the footnote's marker (e.g. `89[`) sits on the exact rule the question asks about. Found
  in the raw page text, `data/processed/pages.jsonl`.
- **By script:** `uv run python eval/check_questions.py --index fixed-1000-150__bge-base --questions
  eval/traps.jsonl` checks that each `extra.footnote` exists in the cleaner's log
  (`data/processed/footnotes_removed.jsonl`) and quotes old text, and that the old-law regex matches the
  footnote but not the current-law reference.

### Results

| | States old law | Correct | Correct or partial | Faithful | Refused |
|---|---|---|---|---|---|
| Footnotes removed | **0/6** | 2/6 | 3/6 | 6/6 | 3/6 |
| Footnotes kept | **2/6** | 3/6 | 3/6 | 5/6 | 1/6 |

"Correct" columns are the judge's grades after two hand corrections (see below). The raw judge grades
are in the run reports: removed [2026-11-02_902d824c](../../results/answers/2026-11-02_902d824c/report.md),
kept [2026-11-02_3e97330d](../../results/answers/2026-11-02_3e97330d/report.md).

The two old-law answers (footnotes kept):

- **t03:** "the penalty is the lesser of 0.5% of the total sales, turnover, or gross receipts ... or
  Rs. 150000 [Section 295]". This is the repealed Section 446, quoted from a footnote, and it cites the
  wrong section (see "Wrong citations" below).
- **t02:** it starts with "No", then gives the old rule that interest is deductible up to 20% of the
  dividends.

Other findings:

- **Wrong citations.** Kept footnotes break section labels. A footnote line such as
  `295. Sub. by the Act ...` looks like the start of Section 295 to the section detector
  ([sections.py](../../../src/income_tax_agent/ingest/sections.py)). So the Section 393 TDS table (p.460)
  is labelled "Section 295", and most retrieved chunks carry that label. Two correct answers cite
  "Section 295": t01 (should be 394) and t06 (should be 393).
- **The refusals (footnotes removed) are mostly retrieval misses.** Plain dense search did not find
  Sections 93 and 428 for t02 and t03. For t01 it found Section 394 twice, but the answer model still
  said "I could not find this". The app's setup (query expansion + reranker) is built for the misses.
- **The Flash-Lite judge made two grading mistakes**, corrected in the table above:
  - kept, t02: it accepted the old 20% rule and graded "partial". Corrected to incorrect.
  - removed, t02: it graded a refusal "correct", against its own rules. Corrected to incorrect.

  It also called the "Section 295" citation in t01 (kept) accurate. The grade (correct) is still right,
  because the judge grades the answer's facts, not its citations.

  The old-law count does not use the judge, so these mistakes don't change it.

## Reproduce

The footnotes-kept index must not overwrite `data/index/fixed-1000-150__bge-base`: the folder name does
not include the cleaning flag. So build it in another folder (here inside the gitignored
`data/processed/`) and point both commands at it with `INDEX_DIR`.

Each command below is the footnotes-kept side. For the footnotes-removed side, run the same command
without `STRIP_FOOTNOTES=false INDEX_DIR=...` (it uses the normal index).

```bash
# Index with footnotes kept (~3 min of local embedding)
STRIP_FOOTNOTES=false INDEX_DIR=data/processed/index-footnotes-kept \
  uv run python -m income_tax_agent.index --chunker fixed

# Check that every trap is tied to an old-text footnote (no API calls)
uv run python eval/check_questions.py --index fixed-1000-150__bge-base --questions eval/traps.jsonl

# Answers on the trap questions (12 Gemini calls per side; cached after the first run)
STRIP_FOOTNOTES=false INDEX_DIR=data/processed/index-footnotes-kept GEMINI_THINKING_LEVEL=minimal \
  uv run python eval/run_eval.py --judge --questions eval/traps.jsonl \
  --index fixed-1000-150__bge-base --modes dense --no-expand --no-rerank --no-neighbours \
  --judge-model gemini-3.5-flash-lite --judge-thinking high
```
