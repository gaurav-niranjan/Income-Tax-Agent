# Retrieval eval: 2026-10-29_9c6155e2

```json
{
  "run_id": "2026-10-29_9c6155e2",
  "kind": "retrieval",
  "created": "2026-10-29T23:29:23",
  "config_hash": "9c6155e2",
  "note": "Structured B1: dense",
  "index": "structured-1500__bge-base",
  "mode": "dense",
  "neighbours": false,
  "depth": 10,
  "strict_share": 0.3,
  "rrf_k": 2,
  "hybrid_candidates": 50,
  "query_prefix": "Represent this sentence for searching relevant passages: ",
  "questions_file": "questions.jsonl",
  "questions_sha": "502ed3c5",
  "n_questions": 26,
  "git_commit": "729e6b5",
  "index_manifest": {
    "name": "structured-1500__bge-base",
    "created": "2026-10-22T08:16:32+00:00",
    "source": {
      "pdf": "Income-tax-Act-2025_2026_2026-08-25_10-41-45_a1d3cd_en.pdf",
      "pages_sha256": "d040fa5f9591e338",
      "n_pages": 674
    },
    "cleaning": {
      "strip_footnotes": true
    },
    "chunker": {
      "type": "structured",
      "max_chars": 1500,
      "min_chars": 300,
      "size_measure": "characters, whitespace runs collapsed",
      "search_prefix": "section + sub-section/table-row label + title (dense + bm25)"
    },
    "embeddings": {
      "type": "fastembed",
      "model": "BAAI/bge-base-en-v1.5",
      "dim": 768,
      "query_prefix": "Represent this sentence for searching relevant passages: "
    },
    "vector_store": {
      "type": "chroma",
      "collection": "chunks",
      "distance": "l2"
    },
    "stats": {
      "n_chunks": 1683,
      "n_chunks_multi_section": 0,
      "chars_total": 1678896,
      "tokens": {
        "min": 20,
        "p50": 256,
        "p90": 343,
        "p99": 393,
        "max": 437,
        "mean": 231.4,
        "over_512": 0
      },
      "embed_seconds": 231.1
    }
  }
}
```

## section-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.62 (16/26) | 0.88 (23/26) | 0.92 (24/26) | 0.74 |
| table | 0.29 (2/7) | 0.71 (5/7) | 0.71 (5/7) | 0.48 |
| definition | 0.80 (4/5) | 1.00 (5/5) | 1.00 (5/5) | 0.90 |
| prose | 0.80 (4/5) | 1.00 (5/5) | 1.00 (5/5) | 0.87 |
| numeric | 0.75 (3/4) | 0.75 (3/4) | 1.00 (4/4) | 0.80 |
| lakh | 0.60 (3/5) | 1.00 (5/5) | 1.00 (5/5) | 0.77 |

## strict-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.62 (16/26) | 0.88 (23/26) | 0.92 (24/26) | 0.74 |
| table | 0.29 (2/7) | 0.71 (5/7) | 0.71 (5/7) | 0.48 |
| definition | 0.80 (4/5) | 1.00 (5/5) | 1.00 (5/5) | 0.90 |
| prose | 0.80 (4/5) | 1.00 (5/5) | 1.00 (5/5) | 0.87 |
| numeric | 0.75 (3/4) | 0.75 (3/4) | 1.00 (4/4) | 0.80 |
| lakh | 0.60 (3/5) | 1.00 (5/5) | 1.00 (5/5) | 0.77 |

## phrase-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.58 (15/26) | 0.73 (19/26) | 0.77 (20/26) | 0.67 |
| table | 0.29 (2/7) | 0.57 (4/7) | 0.57 (4/7) | 0.43 |
| definition | 0.80 (4/5) | 0.80 (4/5) | 0.80 (4/5) | 0.83 |
| prose | 0.80 (4/5) | 0.80 (4/5) | 0.80 (4/5) | 0.80 |
| numeric | 0.75 (3/4) | 0.75 (3/4) | 1.00 (4/4) | 0.80 |
| lakh | 0.40 (2/5) | 0.80 (4/5) | 0.80 (4/5) | 0.62 |

## Per question (first-hit rank; - = none in top 10)

| id | type | section | strict | phrase | expected | top-3 retrieved sections |
|---|---|---|---|---|---|---|
| q01 | table | 2 | 2 | 2 | 202 | 2; 202; 202 |
| q02 | table | 1 | 1 | 1 | 393 | 393; 402; Schedule III |
| q03 | table | 1 | 1 | 1 | 394 | 394; 33; 394 |
| q04 | table | 2 | 2 | 6 | 263 | 352; 263; 352 |
| q05 | table | 3 | 3 | 3 | 19 | 29; 93; 19 |
| q06 | table | - | - | - | 394 | 402; 193; 209 |
| q07 | definition | 1 | 1 | 1 | 2 | 2; 402; 318 |
| q08 | definition | 1 | 1 | 1 | 2 | 2; 402; 263 |
| q09 | definition | 1 | 1 | 1 | 3 | 3; 2; 184 |
| q10 | definition | 2 | 2 | 1 | 2,92 | 515; 2; 184 |
| q11 | prose | 1 | 1 | 1 | 6 | 6; 6; 2 |
| q12 | prose | 1 | 1 | 1 | 1 | 1; 536; 535 |
| q13 | prose | 1 | 1 | 1 | 202 | 202; 333; 199 |
| q14 | prose | 1 | 1 | 1 | 536 | 536; 536; 536 |
| q15 | numeric | 1 | 1 | 1 | 126 | 126; 126; 126 |
| q16 | numeric | 1 | 1 | 1 | 126 | 126; 126; 126 |
| q17 | numeric | 5 | 5 | 5 | 22 | 20; 134; 142 |
| q18 | numeric | 1 | 1 | 1 | 156 | 156; 155; 393 |
| q19 | lakh | 1 | 1 | 1 | 202 | 202; 201; 202 |
| q20 | lakh | 1 | 1 | 1 | 156 | 156; 155; 5 |
| q21 | lakh | 3 | 3 | 8 | 198 | 197; 197; 198 |
| q22 | lakh | 1 | 1 | 2 | 123,Schedule XV | Schedule XV; 123; Schedule XV |
| q27 | prose | 3 | 3 | - | 212,213,214,215,216,217 | 211; 6; 213 |
| q28 | table | - | - | - | 194 | 446; 509; 509 |
| q29 | lakh | 2 | 2 | 2 | 109,202 | 110; 109; 108 |
| q30 | definition | 1 | 1 | 6 | 2 | 2; 197; 288 |
