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
  "git_commit": "ded466e",
  "index_manifest": {
    "name": "fixed-1000-150-header__bge-base",
    "created": "2026-10-18T11:55:41+00:00",
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
      "search_prefix": "section header (dense + bm25)"
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
      "embed_seconds": 199.5
    }
  }
}
```

## section-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.64 (14/22) | 0.77 (17/22) | 0.86 (19/22) | 0.73 |
| table | 0.50 (3/6) | 0.83 (5/6) | 1.00 (6/6) | 0.71 |
| definition | 0.00 (0/4) | 0.00 (0/4) | 0.25 (1/4) | 0.14 |
| prose | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |
| numeric | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.83 |
| lakh | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |

## strict-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.64 (14/22) | 0.77 (17/22) | 0.86 (19/22) | 0.73 |
| table | 0.50 (3/6) | 0.83 (5/6) | 1.00 (6/6) | 0.71 |
| definition | 0.00 (0/4) | 0.00 (0/4) | 0.25 (1/4) | 0.14 |
| prose | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |
| numeric | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.83 |
| lakh | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |

## phrase-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.50 (11/22) | 0.77 (17/22) | 0.86 (19/22) | 0.64 |
| table | 0.50 (3/6) | 0.67 (4/6) | 0.83 (5/6) | 0.62 |
| definition | 0.25 (1/4) | 0.25 (1/4) | 0.50 (2/4) | 0.35 |
| prose | 0.50 (2/4) | 1.00 (4/4) | 1.00 (4/4) | 0.67 |
| numeric | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.83 |
| lakh | 0.50 (2/4) | 1.00 (4/4) | 1.00 (4/4) | 0.75 |

## Per question (first-hit rank; - = none in top 10)

| id | type | section | strict | phrase | expected | top-3 retrieved sections |
|---|---|---|---|---|---|---|
| q01 | table | 1 | 1 | 1 | 202 | 201,202; 201,202; 202 |
| q02 | table | 2 | 2 | 2 | 393 | 2; 393; 393 |
| q03 | table | 1 | 1 | 1 | 394 | 394; 394; 393 |
| q04 | table | 2 | 2 | - | 263 | 423; 262,263; 263 |
| q05 | table | 4 | 4 | 4 | 19 | 201,202; 146; 202 |
| q06 | table | 1 | 1 | 1 | 394 | 394; 402; Schedule II |
| q07 | definition | 6 | 6 | 6 | 2 | 99,100; 303; 402 |
| q08 | definition | - | - | - | 2 | 393; 402; 393 |
| q09 | definition | 4 | 4 | 4 | 3 | 60; 279; 146 |
| q10 | definition | 7 | 7 | 1 | 2,92 | 515,516; 515; 355 |
| q11 | prose | 1 | 1 | 3 | 6 | 6; 6; 5,6 |
| q12 | prose | 1 | 1 | 1 | 1 | 1,2; 536; 352 |
| q13 | prose | 1 | 1 | 3 | 202 | 202,203; 201,202; 202 |
| q14 | prose | 1 | 1 | 1 | 536 | 535,536; 536; 536 |
| q15 | numeric | 1 | 1 | 1 | 126 | 126; 126; 126 |
| q16 | numeric | 1 | 1 | 1 | 126 | 126; 126; 126 |
| q17 | numeric | 3 | 3 | 3 | 22 | 142; 141,142; 22 |
| q18 | numeric | 1 | 1 | 1 | 156 | 155,156; 154,155,156; 2 |
| q19 | lakh | 1 | 1 | 2 | 202 | 201,202; 202; 156,157 |
| q20 | lakh | 1 | 1 | 1 | 156 | 155,156; 156,157; 154,155,156 |
| q21 | lakh | 1 | 1 | 2 | 198 | 197,198; 198; 197 |
| q22 | lakh | 1 | 1 | 1 | 123,Schedule XV | 122,123,124; Schedule XV; 122,123 |
