# Retrieval eval: 2026-11-02_cb3ad3c8

```json
{
  "run_id": "2026-11-02_cb3ad3c8",
  "kind": "retrieval",
  "created": "2026-11-02T13:47:56",
  "config_hash": "cb3ad3c8",
  "note": "Footnotes removed (ablation pair)",
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
| all | 0.20 (2/10) | 0.50 (5/10) | 0.60 (6/10) | 0.39 |
| table | 0.00 (0/2) | 0.50 (1/2) | 0.50 (1/2) | 0.25 |
| definition | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| prose | 0.00 (0/2) | 0.00 (0/2) | 0.50 (1/2) | 0.18 |
| numeric | 0.00 (0/2) | 0.50 (1/2) | 0.50 (1/2) | 0.25 |
| lakh | 0.00 (0/2) | 0.50 (1/2) | 0.50 (1/2) | 0.25 |

## strict-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.20 (2/10) | 0.40 (4/10) | 0.60 (6/10) | 0.36 |
| table | 0.00 (0/2) | 0.50 (1/2) | 0.50 (1/2) | 0.25 |
| definition | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| prose | 0.00 (0/2) | 0.00 (0/2) | 0.50 (1/2) | 0.18 |
| numeric | 0.00 (0/2) | 0.00 (0/2) | 0.50 (1/2) | 0.12 |
| lakh | 0.00 (0/2) | 0.50 (1/2) | 0.50 (1/2) | 0.25 |

## phrase-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.10 (1/10) | 0.40 (4/10) | 0.40 (4/10) | 0.25 |
| table | 0.00 (0/2) | 0.50 (1/2) | 0.50 (1/2) | 0.17 |
| definition | 0.50 (1/2) | 1.00 (2/2) | 1.00 (2/2) | 0.75 |
| prose | 0.00 (0/2) | 0.00 (0/2) | 0.00 (0/2) | 0.00 |
| numeric | 0.00 (0/2) | 0.00 (0/2) | 0.00 (0/2) | 0.08 |
| lakh | 0.00 (0/2) | 0.50 (1/2) | 0.50 (1/2) | 0.25 |

## Per question (first-hit rank; - = none in top 10)

| id | type | section | strict | phrase | expected | top-3 retrieved sections |
|---|---|---|---|---|---|---|
| h01 | table | - | - | - | 196 | Schedule VI; 208,209; 207,208 |
| h02 | table | 2 | 2 | 3 | 408 | 406,407; 407,408; 408 |
| h03 | definition | 1 | 1 | 1 | 17 | 17; Schedule III; 92 |
| h04 | definition | 1 | 1 | 2 | 129 | 128,129; 129,130; 129 |
| h05 | prose | 4 | 4 | - | 82 | 110,111; 86; 85,86 |
| h06 | prose | 9 | 9 | - | 267 | 424,425; 437; 398 |
| h07 | numeric | 2 | 4 | 6 | 154 | 127; 154,155,156; 127 |
| h08 | numeric | - | - | - | 428 | 425; 425; 352 |
| h09 | lakh | - | - | - | 186 | 402; 393; 476 |
| h10 | lakh | 2 | 2 | 2 | 58 | 63; 58; 60,61 |
