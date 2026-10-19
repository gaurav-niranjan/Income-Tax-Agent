# Retrieval eval: 2026-10-19_e31f3f77

```json
{
  "run_id": "2026-10-19_e31f3f77",
  "kind": "retrieval",
  "created": "2026-10-19T12:54:15",
  "config_hash": "e31f3f77",
  "note": "held-out",
  "index": "fixed-1000-150-header__bge-base",
  "mode": "dense",
  "neighbours": true,
  "depth": 10,
  "strict_share": 0.3,
  "rrf_k": 60,
  "hybrid_candidates": 50,
  "query_prefix": "Represent this sentence for searching relevant passages: ",
  "questions_file": "heldout.jsonl",
  "questions_sha": "39d7c570",
  "n_questions": 10,
  "git_commit": "741d29e",
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
| all | 0.60 (6/10) | 0.70 (7/10) | 0.80 (8/10) | 0.67 |
| table | 0.00 (0/2) | 0.50 (1/2) | 1.00 (2/2) | 0.27 |
| definition | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| prose | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.58 |
| numeric | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| lakh | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.50 |

## strict-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.60 (6/10) | 0.70 (7/10) | 0.80 (8/10) | 0.67 |
| table | 0.00 (0/2) | 0.50 (1/2) | 1.00 (2/2) | 0.27 |
| definition | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| prose | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.58 |
| numeric | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| lakh | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.50 |

## phrase-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.50 (5/10) | 0.70 (7/10) | 0.80 (8/10) | 0.62 |
| table | 0.00 (0/2) | 0.50 (1/2) | 1.00 (2/2) | 0.27 |
| definition | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| prose | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.58 |
| numeric | 0.50 (1/2) | 1.00 (2/2) | 1.00 (2/2) | 0.75 |
| lakh | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.50 |

## Per question (first-hit rank; - = none in top 10)

| id | type | section | strict | phrase | expected | top-3 retrieved sections |
|---|---|---|---|---|---|---|
| h01 | table | 5 | 5 | 5 | 196 | 207,208; 207,208; 208 |
| h02 | table | 3 | 3 | 3 | 408 | 424,425; 425; 425 |
| h03 | definition | 1 | 1 | 1 | 17 | 16,17; 17; 17 |
| h04 | definition | 1 | 1 | 1 | 129 | 129; 129,130; 129,130 |
| h05 | prose | 6 | 6 | 6 | 82 | 86; 86; 86 |
| h06 | prose | 1 | 1 | 1 | 267 | 267; 267; 267 |
| h07 | numeric | 1 | 1 | 2 | 154 | 154; 154,155,156; 155,156 |
| h08 | numeric | 1 | 1 | 1 | 428 | 427,428; 428; 428,429 |
| h09 | lakh | - | - | - | 186 | Schedule III; Schedule III; Schedule III |
| h10 | lakh | 1 | 1 | 1 | 58 | 57,58; 58; 58 |
