# Retrieval eval: 2026-11-02_c432e46d

```json
{
  "run_id": "2026-11-02_c432e46d",
  "kind": "retrieval",
  "created": "2026-11-02T13:47:54",
  "config_hash": "c432e46d",
  "note": "Footnotes kept (ablation)",
  "index": "fixed-1000-150__bge-base",
  "mode": "dense",
  "neighbours": false,
  "depth": 10,
  "strict_share": 0.3,
  "rrf_k": 2,
  "hybrid_candidates": 50,
  "query_prefix": "Represent this sentence for searching relevant passages: ",
  "questions_file": "heldout.jsonl",
  "questions_sha": "39d7c570",
  "n_questions": 10,
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
| all | 0.40 (4/10) | 0.70 (7/10) | 0.70 (7/10) | 0.53 |
| table | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.50 |
| definition | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| prose | 0.50 (1/2) | 1.00 (2/2) | 1.00 (2/2) | 0.67 |
| numeric | 0.00 (0/2) | 0.50 (1/2) | 0.50 (1/2) | 0.25 |
| lakh | 0.00 (0/2) | 0.50 (1/2) | 0.50 (1/2) | 0.25 |

## strict-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.40 (4/10) | 0.60 (6/10) | 0.70 (7/10) | 0.51 |
| table | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.50 |
| definition | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| prose | 0.50 (1/2) | 1.00 (2/2) | 1.00 (2/2) | 0.67 |
| numeric | 0.00 (0/2) | 0.00 (0/2) | 0.50 (1/2) | 0.12 |
| lakh | 0.00 (0/2) | 0.50 (1/2) | 0.50 (1/2) | 0.25 |

## phrase-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.40 (4/10) | 0.60 (6/10) | 0.60 (6/10) | 0.53 |
| table | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| definition | 0.50 (1/2) | 1.00 (2/2) | 1.00 (2/2) | 0.75 |
| prose | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.58 |
| numeric | 0.00 (0/2) | 0.00 (0/2) | 0.00 (0/2) | 0.08 |
| lakh | 0.00 (0/2) | 0.50 (1/2) | 0.50 (1/2) | 0.25 |

## Per question (first-hit rank; - = none in top 10)

| id | type | section | strict | phrase | expected | top-3 retrieved sections |
|---|---|---|---|---|---|---|
| h01 | table | 1 | 1 | 1 | 196 | 196; 208,209; 73 |
| h02 | table | - | - | 1 | 408 | 295; 295; 295 |
| h03 | definition | 1 | 1 | 1 | 17 | 17; 92; 92 |
| h04 | definition | 1 | 1 | 2 | 129 | 128,129; 129,130; 129 |
| h05 | prose | 3 | 3 | 6 | 82 | 109,110; 86; 82,83 |
| h06 | prose | 1 | 1 | 1 | 267 | 267; 295; 295 |
| h07 | numeric | 2 | 4 | 6 | 154 | 127; 154,155,156; 127 |
| h08 | numeric | - | - | - | 428 | 295; 295; 295 |
| h09 | lakh | - | - | - | 186 | 85; 295; Schedule III |
| h10 | lakh | 2 | 2 | 2 | 58 | 63; 58; 60,61 |
