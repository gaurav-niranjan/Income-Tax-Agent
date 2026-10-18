# Retrieval eval: 2026-10-18_44c7ee3b

```json
{
  "run_id": "2026-10-18_44c7ee3b",
  "kind": "retrieval",
  "created": "2026-10-18T16:40:15",
  "config_hash": "44c7ee3b",
  "note": "baseline index",
  "index": "fixed-1000-150__bge-base",
  "mode": "hybrid",
  "neighbours": false,
  "depth": 10,
  "strict_share": 0.3,
  "rrf_k": 60,
  "hybrid_candidates": 50,
  "query_prefix": "Represent this sentence for searching relevant passages: ",
  "questions_file": "questions.jsonl",
  "questions_sha": "5826d3f4",
  "n_questions": 22,
  "git_commit": "7abc2f3",
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
| all | 0.59 (13/22) | 0.82 (18/22) | 0.91 (20/22) | 0.73 |
| table | 0.67 (4/6) | 1.00 (6/6) | 1.00 (6/6) | 0.83 |
| definition | 0.00 (0/4) | 0.25 (1/4) | 0.50 (2/4) | 0.20 |
| prose | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |
| numeric | 0.75 (3/4) | 0.75 (3/4) | 1.00 (4/4) | 0.80 |
| lakh | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |

## strict-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.59 (13/22) | 0.82 (18/22) | 0.91 (20/22) | 0.73 |
| table | 0.67 (4/6) | 1.00 (6/6) | 1.00 (6/6) | 0.83 |
| definition | 0.00 (0/4) | 0.25 (1/4) | 0.50 (2/4) | 0.20 |
| prose | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |
| numeric | 0.75 (3/4) | 0.75 (3/4) | 1.00 (4/4) | 0.80 |
| lakh | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |

## phrase-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.55 (12/22) | 0.68 (15/22) | 0.77 (17/22) | 0.64 |
| table | 0.50 (3/6) | 0.83 (5/6) | 0.83 (5/6) | 0.67 |
| definition | 0.25 (1/4) | 0.25 (1/4) | 0.50 (2/4) | 0.37 |
| prose | 0.75 (3/4) | 0.75 (3/4) | 0.75 (3/4) | 0.75 |
| numeric | 0.75 (3/4) | 0.75 (3/4) | 1.00 (4/4) | 0.80 |
| lakh | 0.50 (2/4) | 0.75 (3/4) | 0.75 (3/4) | 0.62 |

## Per question (first-hit rank; - = none in top 10)

| id | type | section | strict | phrase | expected | top-3 retrieved sections |
|---|---|---|---|---|---|---|
| q01 | table | 1 | 1 | 1 | 202 | 201,202; 198,199; 160 |
| q02 | table | 1 | 1 | 1 | 393 | 393; 2; 393 |
| q03 | table | 1 | 1 | 1 | 394 | 394; 393; 395 |
| q04 | table | 1 | 1 | - | 263 | 262,263; 423; 204,205 |
| q05 | table | 2 | 2 | 2 | 19 | 198,199; 18,19; 141,142 |
| q06 | table | 2 | 2 | 2 | 394 | 402; 394; Schedule XV |
| q07 | definition | 7 | 7 | 7 | 2 | 288; 99,100; 302,303 |
| q08 | definition | 7 | 7 | 7 | 2 | 128,129; 402; 152,153 |
| q09 | definition | 5 | 5 | 5 | 3 | 60; 63; 403,404,405 |
| q10 | definition | 3 | 3 | 1 | 2,92 | 515,516; 355; 2 |
| q11 | prose | 1 | 1 | 1 | 6 | 5,6; 6; 6 |
| q12 | prose | 1 | 1 | 1 | 1 | 1,2; 536; 529,530,531 |
| q13 | prose | 2 | 2 | - | 202 | 198,199; 201,202; 87 |
| q14 | prose | 1 | 1 | 1 | 536 | 535,536; 536; 341 |
| q15 | numeric | 1 | 1 | 1 | 126 | 126; 126; 125,126 |
| q16 | numeric | 1 | 1 | 1 | 126 | 126; 126; 126 |
| q17 | numeric | 5 | 5 | 5 | 22 | 23,24,25; 141,142; 142 |
| q18 | numeric | 1 | 1 | 1 | 156 | 155,156; 154,155,156; 196 |
| q19 | lakh | 2 | 2 | - | 202 | 156,157; 201,202; 393 |
| q20 | lakh | 1 | 1 | 1 | 156 | 155,156; 156,157; 62 |
| q21 | lakh | 1 | 1 | 1 | 198 | 198; 69; 210 |
| q22 | lakh | 1 | 1 | 2 | 123,Schedule XV | Schedule XIV,Schedule XV; 122,123,124; Schedule II |
