# Retrieval eval: 2026-11-02_67218604

```json
{
  "run_id": "2026-11-02_67218604",
  "kind": "retrieval",
  "created": "2026-11-02T13:47:51",
  "config_hash": "67218604",
  "note": "Footnotes kept (ablation)",
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
  "git_commit": "6b6a66c",
  "index_manifest": {
    "name": "fixed-1000-150__bge-base",
    "created": "2026-11-02T08:17:38+00:00",
    "source": {
      "pdf": "Income-tax-Act-2025_2026_2026-08-25_10-41-45_a1d3cd_en.pdf",
      "pages_sha256": "d040fa5f9591e338",
      "n_pages": 674
    },
    "cleaning": {
      "strip_footnotes": false
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
      "n_chunks": 2193,
      "n_chunks_multi_section": 344,
      "chars_total": 1736634,
      "tokens": {
        "min": 87,
        "p50": 204,
        "p90": 232,
        "p99": 266,
        "max": 378,
        "mean": 202.8,
        "over_512": 0
      },
      "embed_seconds": 194.9
    }
  }
}
```

## section-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.58 (15/26) | 0.62 (16/26) | 0.69 (18/26) | 0.62 |
| table | 0.29 (2/7) | 0.29 (2/7) | 0.29 (2/7) | 0.31 |
| definition | 0.60 (3/5) | 0.60 (3/5) | 0.60 (3/5) | 0.60 |
| prose | 0.60 (3/5) | 0.60 (3/5) | 0.80 (4/5) | 0.65 |
| numeric | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |
| lakh | 0.60 (3/5) | 0.80 (4/5) | 1.00 (5/5) | 0.74 |

## strict-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.58 (15/26) | 0.62 (16/26) | 0.69 (18/26) | 0.62 |
| table | 0.29 (2/7) | 0.29 (2/7) | 0.29 (2/7) | 0.31 |
| definition | 0.60 (3/5) | 0.60 (3/5) | 0.60 (3/5) | 0.60 |
| prose | 0.60 (3/5) | 0.60 (3/5) | 0.80 (4/5) | 0.65 |
| numeric | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |
| lakh | 0.60 (3/5) | 0.80 (4/5) | 1.00 (5/5) | 0.74 |

## phrase-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.54 (14/26) | 0.62 (16/26) | 0.65 (17/26) | 0.59 |
| table | 0.43 (3/7) | 0.43 (3/7) | 0.43 (3/7) | 0.43 |
| definition | 0.60 (3/5) | 0.60 (3/5) | 0.60 (3/5) | 0.60 |
| prose | 0.40 (2/5) | 0.40 (2/5) | 0.60 (3/5) | 0.45 |
| numeric | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.83 |
| lakh | 0.60 (3/5) | 0.80 (4/5) | 0.80 (4/5) | 0.73 |

## Per question (first-hit rank; - = none in top 10)

| id | type | section | strict | phrase | expected | top-3 retrieved sections |
|---|---|---|---|---|---|---|
| q01 | table | 1 | 1 | 1 | 202 | 202; 295; 201 |
| q02 | table | - | - | 1 | 393 | 295; 2; 295 |
| q03 | table | - | - | 1 | 394 | 295; 33; 38 |
| q04 | table | 1 | 1 | - | 263 | 262,263; 263; 263 |
| q05 | table | - | - | - | 19 | 206; 124; 60 |
| q06 | table | - | - | - | 394 | 295; 207,208; 198 |
| q07 | definition | 1 | 1 | 1 | 2 | 2; 46; 127 |
| q08 | definition | - | - | - | 2 | 295; 128,129; Schedule XV |
| q09 | definition | 1 | 1 | 1 | 3 | 3,4; Schedule XV; 295 |
| q10 | definition | 1 | 1 | 1 | 2,92 | 92,93; 162; 295 |
| q11 | prose | 1 | 1 | 1 | 6 | 6; 6; 6 |
| q12 | prose | 1 | 1 | 1 | 1 | 1,2; 295; 295 |
| q13 | prose | 1 | 1 | - | 202 | 202,203; 295; 200,201 |
| q14 | prose | - | - | 4 | 536 | 295; 295; 295 |
| q15 | numeric | 1 | 1 | 3 | 126 | 125,126; Schedule XIV,Schedule XV; 126 |
| q16 | numeric | 1 | 1 | 1 | 126 | 126; 126; 126 |
| q17 | numeric | 1 | 1 | 1 | 22 | 21,22; 28; 26,27,28 |
| q18 | numeric | 1 | 1 | 1 | 156 | 155,156; 154,155,156; 2 |
| q19 | lakh | 2 | 2 | 2 | 202 | 156,157; 202; 295 |
| q20 | lakh | 1 | 1 | 1 | 156 | 155,156; 156,157; 295 |
| q21 | lakh | 5 | 5 | 6 | 198 | 210; 85; 214,215 |
| q22 | lakh | 1 | 1 | 1 | 123,Schedule XV | 123,124; Schedule XIV,Schedule XV; Schedule II |
| q27 | prose | 4 | 4 | - | 212,213,214,215,216,217 | 160; Schedule IV; 9 |
| q28 | table | 6 | 6 | - | 194 | 295; 295; Schedule IV |
| q29 | lakh | 1 | 1 | 1 | 109,202 | 109,110; 108,109; 111,112 |
| q30 | definition | - | - | - | 2 | Schedule XVI; 85,86; Schedule V |
