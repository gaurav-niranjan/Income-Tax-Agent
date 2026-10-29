# Retrieval eval: 2026-10-29_4b919220

```json
{
  "run_id": "2026-10-29_4b919220",
  "kind": "retrieval",
  "created": "2026-10-29T17:21:54",
  "config_hash": "4b919220",
  "note": "Ladder 1: baseline",
  "index": "fixed-1000-150__bge-base",
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
| all | 0.54 (14/26) | 0.65 (17/26) | 0.77 (20/26) | 0.64 |
| table | 0.43 (3/7) | 0.43 (3/7) | 0.57 (4/7) | 0.50 |
| definition | 0.40 (2/5) | 0.60 (3/5) | 0.60 (3/5) | 0.50 |
| prose | 0.60 (3/5) | 0.80 (4/5) | 1.00 (5/5) | 0.74 |
| numeric | 0.75 (3/4) | 0.75 (3/4) | 1.00 (4/4) | 0.81 |
| lakh | 0.60 (3/5) | 0.80 (4/5) | 0.80 (4/5) | 0.73 |

## strict-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.54 (14/26) | 0.65 (17/26) | 0.77 (20/26) | 0.64 |
| table | 0.43 (3/7) | 0.43 (3/7) | 0.57 (4/7) | 0.50 |
| definition | 0.40 (2/5) | 0.60 (3/5) | 0.60 (3/5) | 0.50 |
| prose | 0.60 (3/5) | 0.80 (4/5) | 1.00 (5/5) | 0.74 |
| numeric | 0.75 (3/4) | 0.75 (3/4) | 1.00 (4/4) | 0.81 |
| lakh | 0.60 (3/5) | 0.80 (4/5) | 0.80 (4/5) | 0.73 |

## phrase-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.50 (13/26) | 0.58 (15/26) | 0.65 (17/26) | 0.56 |
| table | 0.29 (2/7) | 0.29 (2/7) | 0.43 (3/7) | 0.34 |
| definition | 0.60 (3/5) | 0.60 (3/5) | 0.60 (3/5) | 0.60 |
| prose | 0.60 (3/5) | 0.60 (3/5) | 0.60 (3/5) | 0.60 |
| numeric | 0.50 (2/4) | 0.75 (3/4) | 1.00 (4/4) | 0.69 |
| lakh | 0.60 (3/5) | 0.80 (4/5) | 0.80 (4/5) | 0.70 |

## Per question (first-hit rank; - = none in top 10)

| id | type | section | strict | phrase | expected | top-3 retrieved sections |
|---|---|---|---|---|---|---|
| q01 | table | 4 | 4 | 4 | 202 | 198,199; 204; 207 |
| q02 | table | 1 | 1 | 1 | 393 | 393; 2; 393 |
| q03 | table | 1 | 1 | 1 | 394 | 394; 33; 38 |
| q04 | table | 1 | 1 | - | 263 | 262,263; 263; 352 |
| q05 | table | - | - | - | 19 | 198,199; 28,29; 124 |
| q06 | table | 10 | 10 | 10 | 394 | 207,208; 207; 209 |
| q07 | definition | 1 | 1 | 1 | 2 | 2; 46; 355 |
| q08 | definition | - | - | - | 2 | 402; 128,129; Schedule XV |
| q09 | definition | 1 | 1 | 1 | 3 | 2,3,4; 143,144; Schedule XV |
| q10 | definition | 2 | 2 | 1 | 2,92 | 515,516; 92,93; 355 |
| q11 | prose | 1 | 1 | 1 | 6 | 5,6; 6; 6 |
| q12 | prose | 1 | 1 | 1 | 1 | 1,2; 536; 536 |
| q13 | prose | 2 | 2 | - | 202 | 319,320; 202,203; 352 |
| q14 | prose | 1 | 1 | 1 | 536 | 535,536; 536; 534,535 |
| q15 | numeric | 1 | 1 | 2 | 126 | 125,126; 126; 126,127 |
| q16 | numeric | 1 | 1 | 1 | 126 | 126; 126; 126 |
| q17 | numeric | 4 | 4 | 4 | 22 | 26,27,28; 23,24,25; 141,142 |
| q18 | numeric | 1 | 1 | 1 | 156 | 155,156; 154,155,156; 198,199 |
| q19 | lakh | 2 | 2 | 3 | 202 | 156,157; 201,202; 202 |
| q20 | lakh | 1 | 1 | 1 | 156 | 155,156; 156,157; 63 |
| q21 | lakh | 6 | 6 | 6 | 198 | 210; 214,215; 69 |
| q22 | lakh | 1 | 1 | 1 | 123,Schedule XV | 122,123,124; Schedule II; Schedule XIV,Schedule XV |
| q27 | prose | 5 | 5 | - | 212,213,214,215,216,217 | 9; 5,6; 9 |
| q28 | table | 6 | 6 | - | 194 | 445,446; 508,509; Schedule IV |
| q29 | lakh | 1 | 1 | 1 | 109,202 | 109,110; 110,111; 86 |
| q30 | definition | - | - | - | 2 | Schedule XVI; 69; 214,215 |
