# Retrieval eval: 2026-10-18_dfd09b28

```json
{
  "run_id": "2026-10-18_dfd09b28",
  "kind": "retrieval",
  "created": "2026-10-18T16:37:47",
  "config_hash": "dfd09b28",
  "note": "baseline index",
  "index": "fixed-1000-150__bge-base",
  "mode": "dense",
  "neighbours": true,
  "depth": 10,
  "strict_share": 0.3,
  "rrf_k": 60,
  "hybrid_candidates": 50,
  "query_prefix": "Represent this sentence for searching relevant passages: ",
  "questions_file": "questions.jsonl",
  "questions_sha": "5826d3f4",
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
| all | 0.59 (13/22) | 0.77 (17/22) | 0.82 (18/22) | 0.71 |
| table | 0.50 (3/6) | 0.50 (3/6) | 0.67 (4/6) | 0.56 |
| definition | 0.50 (2/4) | 0.75 (3/4) | 0.75 (3/4) | 0.62 |
| prose | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |
| numeric | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |
| lakh | 0.50 (2/4) | 0.75 (3/4) | 0.75 (3/4) | 0.67 |

## strict-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.59 (13/22) | 0.77 (17/22) | 0.82 (18/22) | 0.71 |
| table | 0.50 (3/6) | 0.50 (3/6) | 0.67 (4/6) | 0.56 |
| definition | 0.50 (2/4) | 0.75 (3/4) | 0.75 (3/4) | 0.62 |
| prose | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |
| numeric | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |
| lakh | 0.50 (2/4) | 0.75 (3/4) | 0.75 (3/4) | 0.67 |

## phrase-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.59 (13/22) | 0.68 (15/22) | 0.82 (18/22) | 0.68 |
| table | 0.33 (2/6) | 0.33 (2/6) | 0.67 (4/6) | 0.43 |
| definition | 0.75 (3/4) | 0.75 (3/4) | 0.75 (3/4) | 0.75 |
| prose | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |
| numeric | 0.75 (3/4) | 0.75 (3/4) | 1.00 (4/4) | 0.81 |
| lakh | 0.50 (2/4) | 0.75 (3/4) | 0.75 (3/4) | 0.67 |

## Per question (first-hit rank; - = none in top 10)

| id | type | section | strict | phrase | expected | top-3 retrieved sections |
|---|---|---|---|---|---|---|
| q01 | table | 4 | 4 | 4 | 202 | 198; 198,199; 199 |
| q02 | table | 1 | 1 | 1 | 393 | 393; 393; 393 |
| q03 | table | 1 | 1 | 1 | 394 | 393,394; 394; 394 |
| q04 | table | 1 | 1 | 4 | 263 | 262,263; 262,263; 263 |
| q05 | table | - | - | - | 19 | 198; 198,199; 199 |
| q06 | table | 10 | 10 | 10 | 394 | 207,208; 207,208; 208 |
| q07 | definition | 1 | 1 | 1 | 2 | 2; 2; 2 |
| q08 | definition | - | - | - | 2 | 402; 402; 402 |
| q09 | definition | 1 | 1 | 1 | 3 | 2; 2,3,4; 3,4,5 |
| q10 | definition | 2 | 2 | 1 | 2,92 | 515; 515,516; 516,517,518,519 |
| q11 | prose | 1 | 1 | 1 | 6 | 5,6; 5,6; 6 |
| q12 | prose | 1 | 1 | 1 | 1 | 1,2; 2; 536 |
| q13 | prose | 2 | 2 | 2 | 202 | 318,319; 319,320; 320 |
| q14 | prose | 1 | 1 | 1 | 536 | 534,535; 535,536; 536 |
| q15 | numeric | 1 | 1 | 1 | 126 | 125; 125,126; 126 |
| q16 | numeric | 1 | 1 | 1 | 126 | 126; 126; 126 |
| q17 | numeric | 2 | 2 | 4 | 22 | 26; 26,27,28; 28,29 |
| q18 | numeric | 1 | 1 | 1 | 156 | 154,155,156; 155,156; 156,157 |
| q19 | lakh | 2 | 2 | 2 | 202 | 155,156; 156,157; 157,158 |
| q20 | lakh | 1 | 1 | 1 | 156 | 154,155,156; 155,156; 156,157 |
| q21 | lakh | 6 | 6 | 6 | 198 | 210; 210; 210 |
| q22 | lakh | 1 | 1 | 1 | 123,Schedule XV | 122,123; 122,123,124; 124 |
