# Retrieval eval: fixed-1000-150__bge-base__hybrid+nb__2026-10-18

```json
{
  "index": "fixed-1000-150__bge-base",
  "mode": "hybrid",
  "neighbours": true,
  "depth": 10,
  "strict_share": 0.3,
  "rrf_k": 60,
  "hybrid_candidates": 50,
  "query_prefix": "Represent this sentence for searching relevant passages: ",
  "questions_file": "questions.jsonl",
  "n_questions": 22,
  "git_commit": "ee84f94",
  "index_manifest": {
    "name": "fixed-1000-150__bge-base",
    "created": "2026-10-18T09:48:16+00:00",
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
      "overlap": 150
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
        "min": 89,
        "p50": 203,
        "p90": 227,
        "p99": 249,
        "max": 313,
        "mean": 200.6,
        "over_512": 0
      },
      "embed_seconds": 185.5
    }
  }
}
```

## section-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.64 (14/22) | 0.86 (19/22) | 0.91 (20/22) | 0.76 |
| table | 0.67 (4/6) | 1.00 (6/6) | 1.00 (6/6) | 0.83 |
| definition | 0.00 (0/4) | 0.25 (1/4) | 0.50 (2/4) | 0.20 |
| prose | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |
| numeric | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |
| lakh | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |

## strict-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.64 (14/22) | 0.86 (19/22) | 0.91 (20/22) | 0.76 |
| table | 0.67 (4/6) | 1.00 (6/6) | 1.00 (6/6) | 0.83 |
| definition | 0.00 (0/4) | 0.25 (1/4) | 0.50 (2/4) | 0.20 |
| prose | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |
| numeric | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |
| lakh | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |

## phrase-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.55 (12/22) | 0.73 (16/22) | 0.82 (18/22) | 0.67 |
| table | 0.50 (3/6) | 0.83 (5/6) | 0.83 (5/6) | 0.67 |
| definition | 0.25 (1/4) | 0.25 (1/4) | 0.50 (2/4) | 0.37 |
| prose | 0.75 (3/4) | 0.75 (3/4) | 0.75 (3/4) | 0.78 |
| numeric | 0.75 (3/4) | 0.75 (3/4) | 1.00 (4/4) | 0.80 |
| lakh | 0.50 (2/4) | 1.00 (4/4) | 1.00 (4/4) | 0.75 |

## Per question (first-hit rank; - = none in top 10)

| id | type | section | strict | phrase | expected | top-3 retrieved sections |
|---|---|---|---|---|---|---|
| q01 | table | 1 | 1 | 1 | 202 | 201,202; 201,202; 202 |
| q02 | table | 1 | 1 | 1 | 393 | 393; 393; 393 |
| q03 | table | 1 | 1 | 1 | 394 | 393,394; 394; 394 |
| q04 | table | 1 | 1 | - | 263 | 262,263; 262,263; 263 |
| q05 | table | 2 | 2 | 2 | 19 | 198; 198,199; 199 |
| q06 | table | 2 | 2 | 2 | 394 | 402; 402; 402 |
| q07 | definition | 7 | 7 | 7 | 2 | 288; 288; 288 |
| q08 | definition | 7 | 7 | 7 | 2 | 128; 128,129; 129 |
| q09 | definition | 5 | 5 | 5 | 3 | 60; 60; 60,61 |
| q10 | definition | 3 | 3 | 1 | 2,92 | 515; 515,516; 516,517,518,519 |
| q11 | prose | 1 | 1 | 1 | 6 | 5,6; 5,6; 6 |
| q12 | prose | 1 | 1 | 1 | 1 | 1,2; 2; 536 |
| q13 | prose | 2 | 2 | 10 | 202 | 198; 198,199; 199 |
| q14 | prose | 1 | 1 | 1 | 536 | 534,535; 535,536; 536 |
| q15 | numeric | 1 | 1 | 1 | 126 | 126; 126; 126 |
| q16 | numeric | 1 | 1 | 1 | 126 | 125,126; 126; 126 |
| q17 | numeric | 1 | 1 | 5 | 22 | 22,23; 23,24,25; 24,25 |
| q18 | numeric | 1 | 1 | 1 | 156 | 154,155,156; 155,156; 156,157 |
| q19 | lakh | 2 | 2 | 2 | 202 | 155,156; 156,157; 157,158 |
| q20 | lakh | 1 | 1 | 1 | 156 | 154,155,156; 155,156; 156,157 |
| q21 | lakh | 1 | 1 | 1 | 198 | 198; 198; 198 |
| q22 | lakh | 1 | 1 | 2 | 123,Schedule XV | Schedule XIV; Schedule XIV,Schedule XV; Schedule XV |
