# Eval results

The steps that shaped the app. **hit@1** = the right section is the first result; **hit@5** = it is in the top 5. A hit is *strict*: the section makes up at least 30% of the chunk. Dev = questions.jsonl, held-out = heldout.jsonl (written later, not used for tuning). With ~23 questions, one question is ~4 points.

Generated from `key_runs.json` by `eval/runs.py` (`uv run python eval/compare.py`). Every run (29 retrieval, 1 answer) is in [all_runs.md](all_runs.md).

## Retrieval: the steps that made it into the app

| step | dev hit@1 | dev hit@5 | dev MRR | held-out hit@1 | held-out hit@5 | held-out MRR | runs |
|---|---|---|---|---|---|---|---|
| Baseline: fixed 1,000-char chunks, dense search | 13/22 | 18/22 | 0.69 | - | - | - | [dev](retrieval/2026-10-18_16a617d8/report.md) |
| + section title in each chunk's search text | 15/22 | 20/22 | 0.76 | - | - | - | [dev](retrieval/2026-10-18_f5a1c02c/report.md) |
| + neighbour chunks + LLM query expansion | 18/22 | 21/22 | 0.87 | - | - | - | [dev](retrieval/2026-10-18_a728fa4a/report.md) |
| Hybrid search, best-rank merge of the queries (app until 2026-10-24) | 18/22 | 21/22 | 0.88 | 8/10 | 10/10 | 0.88 | [dev](retrieval/2026-10-19_7904715b/report.md) · [held-out](retrieval/2026-10-19_73ee91cf/report.md) |
| Structured chunks, same setup | 18/22 | 22/22 | 0.89 | 8/10 | 10/10 | 0.86 | [dev](retrieval/2026-10-22_28619463/report.md) · [held-out](retrieval/2026-10-22_031da53e/report.md) |
| Same, NRI question added (23 dev questions from here): NRI missed | 18/23 | 22/23 | 0.86 | 8/10 | 10/10 | 0.86 | [dev](retrieval/2026-10-24_83fc945a/report.md) · [held-out](retrieval/2026-10-24_031da53e/report.md) |
| Rejected: chapter and part headings in the search text | 16/23 | 21/23 | 0.79 | 8/10 | 10/10 | 0.87 | [dev](retrieval/2026-10-24_4720f604/report.md) · [held-out](retrieval/2026-10-24_ed8d463b/report.md) |
| + reranker (MiniLM-L-6), scored against the question | 20/23 | 23/23 | 0.93 | 8/10 | 9/10 | 0.83 | [dev](retrieval/2026-10-24_9625e7ac/report.md) · [held-out](retrieval/2026-10-24_70cf942b/report.md) |
| + half the best rewrite's score added | 22/23 | 23/23 | 0.98 | 8/10 | 10/10 | 0.88 | [dev](retrieval/2026-10-24_95ee347c/report.md) · [held-out](retrieval/2026-10-24_bbf61ac4/report.md) |
| **Dense first stage, 10 candidates per query (the app)** | 23/23 | 23/23 | 1.00 | 9/10 | 10/10 | 0.93 | [dev](retrieval/2026-10-24_6e9351f7/report.md) · [held-out](retrieval/2026-10-24_63c7a818/report.md) |

## Retrieval: also tried

| step | dev hit@1 | dev hit@5 | dev MRR | held-out hit@1 | held-out hit@5 | held-out MRR | runs |
|---|---|---|---|---|---|---|---|
| BM25 (keywords) only, baseline chunks | 11/22 | 16/22 | 0.61 | - | - | - | [dev](retrieval/2026-10-18_7caffad9/report.md) |
| Hybrid with the standard RRF k=60, baseline chunks | 13/22 | 20/22 | 0.73 | - | - | - | [dev](retrieval/2026-10-18_44c7ee3b/report.md) |
| Bigger reranker: MiniLM-L-12 (120 MB), scored against the question | 16/23 | 23/23 | 0.85 | 8/10 | 9/10 | 0.83 | [dev](retrieval/2026-10-24_403189e8/report.md) · [held-out](retrieval/2026-10-24_78f3198a/report.md) |
| Bigger reranker: jina-reranker-v1-turbo (150 MB), same | 16/23 | 21/23 | 0.80 | 6/10 | 9/10 | 0.72 | [dev](retrieval/2026-10-24_43b7cbb8/report.md) · [held-out](retrieval/2026-10-24_b9fd4f9b/report.md) |
| Bigger reranker: bge-reranker-base (1 GB, 8x slower), same | 19/23 | 23/23 | 0.90 | 4/10 | 10/10 | 0.64 | [dev](retrieval/2026-10-24_7adda55f/report.md) · [held-out](retrieval/2026-10-24_0a3c6fb9/report.md) |
| App setup on fixed chunks instead of structured (20 candidates) | 19/23 | 22/23 | 0.87 | 7/10 | 10/10 | 0.82 | [dev](retrieval/2026-10-24_d0349a98/report.md) · [held-out](retrieval/2026-10-24_6fee4b4e/report.md) |
| App setup without query expansion (20 candidates) | 21/23 | 22/23 | 0.93 | 8/10 | 9/10 | 0.83 | [dev](retrieval/2026-10-24_3ef3dcd7/report.md) · [held-out](retrieval/2026-10-24_cf10af4d/report.md) |

## Answers (LLM judge)

Correct and false refusals are over judged in-scope questions; faithful over all judged ones.

| step | judged | correct | correct or partial | faithful | false refusals | run |
|---|---|---|---|---|---|---|
| First answer eval, old app setup (judge quota ran out at 18/26) | 18/26 | 0.50 (9/18) | 0.83 (15/18) | 0.94 (17/18) | 0.17 (3/18) | [2026-10-18_d4acdb36](answers/2026-10-18_d4acdb36/report.md) |
