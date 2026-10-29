# Eval results

The steps that shaped the app. **hit@1** = the right section is the first result; **hit@5** = it is in the top 5; **MRR** = the mean of 1/rank of the first right result (1.00 = always first). A hit is *strict*: the section makes up at least 30% of the chunk. Dev = questions.jsonl, held-out = heldout.jsonl (written later, not used for tuning). Counts are questions: with this few, one question moves a rate by several points.

Generated from `key_runs.json` by `eval/runs.py` (`uv run python eval/compare.py`). Every run (55 retrieval, 1 answer) is in [all_runs.md](all_runs.md).

## Retrieval: how the app was built

- **search**: dense = embedding similarity; hybrid = dense + BM25 keyword search, merged with RRF.
- **query expansion**: Gemini writes 3 extra search queries in the Act's wording; the question is searched too. Without a reranker, their result lists are merged (RRF in the earliest runs, best rank later).
- **reranker**: a cross-encoder reads the question next to each pooled chunk and orders them. *question + half of best rewrite* = its score against the question plus half its best score against a rewrite.
- **neighbours**: the chunks before and after each hit, if in the same section. On structured chunks that is always so, so they can't change these metrics; they give the answer model the rest of a sub-section or table.

### A. Fixed 1,000-character chunks (how the app started)

The original steps, each run with the settings it had then. A3 added two things at once; A4 also changed how the queries' lists are merged (RRF with k=60, 20 candidates each -> best rank, 10 candidates each).

| # | step | search | query expansion | reranker | neighbours | dev hit@1 | dev hit@5 | dev MRR | held-out hit@1 | held-out hit@5 | held-out MRR | runs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 | Baseline | dense | – | – | – | 14/26 | 20/26 | 0.64 | 2/10 | 6/10 | 0.36 | [dev](retrieval/2026-10-29_4b919220/report.md) · [held-out](retrieval/2026-10-29_cb3ad3c8/report.md) |
| A2 | + section title in each chunk | dense | – | – | – | 16/26 | 22/26 | 0.70 | 5/10 | 8/10 | 0.62 | [dev](retrieval/2026-10-29_049d1a76/report.md) · [held-out](retrieval/2026-10-29_bfc98597/report.md) |
| A3 | + query expansion, + neighbours | dense | ✓ | – | ✓ | 20/26 | 24/26 | 0.83 | 8/10 | 9/10 | 0.83 | [dev](retrieval/2026-10-29_e5d30f8b/report.md) · [held-out](retrieval/2026-10-29_338afafa/report.md) |
| A4 | + hybrid search (dense + BM25) | hybrid | ✓ | – | ✓ | 19/26 | 24/26 | 0.83 | 8/10 | 10/10 | 0.88 | [dev](retrieval/2026-10-29_e4036857/report.md) · [held-out](retrieval/2026-10-29_73ee91cf/report.md) |

### B. Structured chunks, one technique at a time (the app)

Today's settings, one technique added per row in the order the pipeline runs them. B5 is the app. The ↳ row changes only the search.

| # | step | search | query expansion | reranker | neighbours | dev hit@1 | dev hit@5 | dev MRR | held-out hit@1 | held-out hit@5 | held-out MRR | runs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | Structured chunks, dense search only | dense | – | – | – | 16/26 | 24/26 | 0.74 | 6/10 | 9/10 | 0.72 | [dev](retrieval/2026-10-29_9c6155e2/report.md) · [held-out](retrieval/2026-10-29_db9be160/report.md) |
| B2 | + query expansion | dense | ✓ | – | – | 20/26 | 25/26 | 0.85 | 8/10 | 10/10 | 0.85 | [dev](retrieval/2026-10-29_b4acecae/report.md) · [held-out](retrieval/2026-10-29_ec10321c/report.md) |
| B3 | + reranker, scored against the question | dense | ✓ | question | – | 22/26 | 25/26 | 0.90 | 8/10 | 9/10 | 0.84 | [dev](retrieval/2026-10-29_7242b726/report.md) · [held-out](retrieval/2026-10-29_ca9c0749/report.md) |
| B4 | + reranker also scores the rewrites | dense | ✓ | question + half of best rewrite | – | 24/26 | 26/26 | 0.96 | 9/10 | 10/10 | 0.93 | [dev](retrieval/2026-10-29_0fbbbfcc/report.md) · [held-out](retrieval/2026-10-29_ba35c7bd/report.md) |
| **B5** | **+ neighbour chunks (the app)** | dense | ✓ | question + half of best rewrite | ✓ | 24/26 | 26/26 | 0.96 | 9/10 | 10/10 | 0.93 | [dev](retrieval/2026-10-29_a16278a2/report.md) · [held-out](retrieval/2026-10-29_63c7a818/report.md) |
| ↳ | B5 with hybrid search, for comparison | hybrid | ✓ | question + half of best rewrite | ✓ | 23/26 | 26/26 | 0.94 | 8/10 | 10/10 | 0.88 | [dev](retrieval/2026-10-29_5b0f44ff/report.md) · [held-out](retrieval/2026-10-29_63a97a31/report.md) |

## Retrieval: also tried

Not re-run: these used the dev set of their time (22 or 23 questions), so compare each one only with the *reference* row above it, which is what it was measured against. The last two used 20 reranker candidates; the app uses 10, which scored the same with dense search.

| step | search | query expansion | reranker | neighbours | dev hit@1 | dev hit@5 | dev MRR | held-out hit@1 | held-out hit@5 | held-out MRR | runs |
|---|---|---|---|---|---|---|---|---|---|---|---|
| *Reference:* baseline (fixed chunks, dense) | dense | – | – | – | 13/22 | 18/22 | 0.69 | - | - | - | [dev](retrieval/2026-10-18_16a617d8/report.md) |
| BM25 (keywords) only, baseline chunks | bm25 | – | – | – | 11/22 | 16/22 | 0.61 | - | - | - | [dev](retrieval/2026-10-18_7caffad9/report.md) |
| Hybrid with the standard RRF k=60, baseline chunks | hybrid | – | – | – | 13/22 | 20/22 | 0.73 | - | - | - | [dev](retrieval/2026-10-18_44c7ee3b/report.md) |
| *Reference:* structured chunks, hybrid + query expansion + neighbours | hybrid | ✓ | – | ✓ | 18/23 | 22/23 | 0.86 | 8/10 | 10/10 | 0.86 | [dev](retrieval/2026-10-24_83fc945a/report.md) · [held-out](retrieval/2026-10-24_031da53e/report.md) |
| Rejected: chapter and part headings in the search text | hybrid | ✓ | – | ✓ | 16/23 | 21/23 | 0.79 | 8/10 | 10/10 | 0.87 | [dev](retrieval/2026-10-24_4720f604/report.md) · [held-out](retrieval/2026-10-24_ed8d463b/report.md) |
| *Reference:* same + reranker (MiniLM-L-6, 80 MB), scored against the question | hybrid | ✓ | question | ✓ | 20/23 | 23/23 | 0.93 | 8/10 | 9/10 | 0.83 | [dev](retrieval/2026-10-24_9625e7ac/report.md) · [held-out](retrieval/2026-10-24_70cf942b/report.md) |
| Bigger reranker: MiniLM-L-12 (120 MB) | hybrid | ✓ | question | ✓ | 16/23 | 23/23 | 0.85 | 8/10 | 9/10 | 0.83 | [dev](retrieval/2026-10-24_403189e8/report.md) · [held-out](retrieval/2026-10-24_78f3198a/report.md) |
| Bigger reranker: jina-reranker-v1-turbo (150 MB) | hybrid | ✓ | question | ✓ | 16/23 | 21/23 | 0.80 | 6/10 | 9/10 | 0.72 | [dev](retrieval/2026-10-24_43b7cbb8/report.md) · [held-out](retrieval/2026-10-24_b9fd4f9b/report.md) |
| Bigger reranker: bge-reranker-base (1 GB, 8x slower) | hybrid | ✓ | question | ✓ | 19/23 | 23/23 | 0.90 | 4/10 | 10/10 | 0.64 | [dev](retrieval/2026-10-24_7adda55f/report.md) · [held-out](retrieval/2026-10-24_0a3c6fb9/report.md) |
| *Reference:* the app at the time | dense | ✓ | question + half of best rewrite | ✓ | 23/23 | 23/23 | 1.00 | 9/10 | 10/10 | 0.93 | [dev](retrieval/2026-10-24_6e9351f7/report.md) · [held-out](retrieval/2026-10-24_63c7a818/report.md) |
| App setup on fixed chunks instead of structured | dense | ✓ | question + half of best rewrite | ✓ | 19/23 | 22/23 | 0.87 | 7/10 | 10/10 | 0.82 | [dev](retrieval/2026-10-24_d0349a98/report.md) · [held-out](retrieval/2026-10-24_6fee4b4e/report.md) |
| App setup without query expansion | dense | – | question + half of best rewrite | ✓ | 21/23 | 22/23 | 0.93 | 8/10 | 9/10 | 0.83 | [dev](retrieval/2026-10-24_3ef3dcd7/report.md) · [held-out](retrieval/2026-10-24_cf10af4d/report.md) |

## Answers (LLM judge)

Correct and false refusals are over judged in-scope questions; faithful over all judged ones.

| step | judged | correct | correct or partial | faithful | false refusals | run |
|---|---|---|---|---|---|---|
| First answer eval, old app setup (judge quota ran out at 18/26) | 18/26 | 0.50 (9/18) | 0.83 (15/18) | 0.94 (17/18) | 0.17 (3/18) | [2026-10-18_d4acdb36](answers/2026-10-18_d4acdb36/report.md) |
