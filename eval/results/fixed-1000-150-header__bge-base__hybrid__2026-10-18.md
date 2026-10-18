# Retrieval eval: fixed-1000-150-header__bge-base__hybrid__2026-10-18

```json
{
  "index": "fixed-1000-150-header__bge-base",
  "mode": "hybrid",
  "neighbours": false,
  "depth": 10,
  "strict_share": 0.3,
  "rrf_k": 60,
  "hybrid_candidates": 50,
  "query_prefix": "Represent this sentence for searching relevant passages: ",
  "questions_file": "questions.jsonl",
  "n_questions": 22,
  "git_commit": "9ab8a79",
  "index_manifest": {
    "name": "fixed-1000-150-header__bge-base",
    "created": "2026-10-18T11:15:43+00:00",
    "source": {
      "pdf": "Income-tax-Act-2025_2026_2026-08-25_10-41-45_a1d3cd_en.pdf",
      "pages_sha256": "d040fa5f9591e338",
      "n_pages": 674
    },
    "cleaning": {
      "strip_footnotes": true
    },
    "chunker": {
      "type": "fixed",
      "size": 1000,
      "overlap": 150,
      "embed_prefix": "section header"
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
      "n_chunks": 2120,
      "n_chunks_multi_section": 575,
      "chars_total": 1678896,
      "tokens": {
        "min": 103,
        "p50": 219,
        "p90": 249,
        "p99": 273,
        "max": 330,
        "mean": 217.3,
        "over_512": 0
      },
      "embed_seconds": 199.4
    }
  }
}
```

## section-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.59 (13/22) | 0.82 (18/22) | 0.86 (19/22) | 0.71 |
| table | 0.67 (4/6) | 1.00 (6/6) | 1.00 (6/6) | 0.81 |
| definition | 0.00 (0/4) | 0.00 (0/4) | 0.25 (1/4) | 0.12 |
| prose | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |
| numeric | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.83 |
| lakh | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |

## strict-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.59 (13/22) | 0.77 (17/22) | 0.86 (19/22) | 0.71 |
| table | 0.67 (4/6) | 1.00 (6/6) | 1.00 (6/6) | 0.81 |
| definition | 0.00 (0/4) | 0.00 (0/4) | 0.25 (1/4) | 0.12 |
| prose | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |
| numeric | 0.75 (3/4) | 0.75 (3/4) | 1.00 (4/4) | 0.81 |
| lakh | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |

## phrase-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.59 (13/22) | 0.68 (15/22) | 0.77 (17/22) | 0.66 |
| table | 0.67 (4/6) | 0.83 (5/6) | 0.83 (5/6) | 0.72 |
| definition | 0.25 (1/4) | 0.25 (1/4) | 0.50 (2/4) | 0.34 |
| prose | 0.50 (2/4) | 0.75 (3/4) | 0.75 (3/4) | 0.66 |
| numeric | 0.75 (3/4) | 0.75 (3/4) | 1.00 (4/4) | 0.81 |
| lakh | 0.75 (3/4) | 0.75 (3/4) | 0.75 (3/4) | 0.75 |

## Per question (first-hit rank; - = none in top 10)

| id | type | section | strict | phrase | expected | top-3 retrieved sections |
|---|---|---|---|---|---|---|
| q01 | table | 1 | 1 | 1 | 202 | 201,202; 201,202; 198,199 |
| q02 | table | 1 | 1 | 1 | 393 | 393; 2; 393 |
| q03 | table | 1 | 1 | 1 | 394 | 394; 393; 393 |
| q04 | table | 2 | 2 | - | 263 | 423; 262,263; 263 |
| q05 | table | 3 | 3 | 3 | 19 | 146; 201,202; 18,19 |
| q06 | table | 1 | 1 | 1 | 394 | 394; 402; Schedule II |
| q07 | definition | 8 | 8 | 8 | 2 | 99,100; 402; 303 |
| q08 | definition | - | - | - | 2 | 393; 402; 393 |
| q09 | definition | 4 | 4 | 4 | 3 | 60; 279; 146 |
| q10 | definition | 8 | 8 | 1 | 2,92 | 515,516; 515; 355 |
| q11 | prose | 1 | 1 | 2 | 6 | 6; 5,6; 6 |
| q12 | prose | 1 | 1 | 1 | 1 | 1,2; 536; 529,530,531 |
| q13 | prose | 2 | 2 | 8 | 202 | 198,199; 201,202; 201,202 |
| q14 | prose | 1 | 1 | 1 | 536 | 535,536; 536; 536 |
| q15 | numeric | 1 | 1 | 1 | 126 | 126; 126; 126 |
| q16 | numeric | 1 | 1 | 1 | 126 | 126; 126; 126 |
| q17 | numeric | 3 | 4 | 4 | 22 | 142; 141,142; 21,22 |
| q18 | numeric | 1 | 1 | 1 | 156 | 155,156; 154,155,156; 2 |
| q19 | lakh | 2 | 2 | - | 202 | 156,157; 201,202; 333,334 |
| q20 | lakh | 1 | 1 | 1 | 156 | 155,156; 156,157; 154,155,156 |
| q21 | lakh | 1 | 1 | 1 | 198 | 198; 197; 197,198 |
| q22 | lakh | 1 | 1 | 1 | 123,Schedule XV | 122,123,124; 122,123; Schedule XIV,Schedule XV |
