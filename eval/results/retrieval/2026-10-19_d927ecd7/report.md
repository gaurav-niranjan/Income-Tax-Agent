# Retrieval eval: 2026-10-19_d927ecd7

```json
{
  "run_id": "2026-10-19_d927ecd7",
  "kind": "retrieval",
  "created": "2026-10-19T14:30:03",
  "config_hash": "d927ecd7",
  "note": "held-out, new fusion",
  "index": "fixed-1000-150-header__bge-base",
  "mode": "bm25",
  "neighbours": true,
  "depth": 10,
  "strict_share": 0.3,
  "rrf_k": 2,
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
| all | 0.50 (5/10) | 0.60 (6/10) | 0.70 (7/10) | 0.60 |
| table | 0.50 (1/2) | 0.50 (1/2) | 1.00 (2/2) | 0.60 |
| definition | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| prose | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.56 |
| numeric | 0.00 (0/2) | 0.50 (1/2) | 0.50 (1/2) | 0.33 |
| lakh | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.50 |

## strict-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.50 (5/10) | 0.60 (6/10) | 0.70 (7/10) | 0.60 |
| table | 0.50 (1/2) | 0.50 (1/2) | 1.00 (2/2) | 0.60 |
| definition | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| prose | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.56 |
| numeric | 0.00 (0/2) | 0.50 (1/2) | 0.50 (1/2) | 0.33 |
| lakh | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.50 |

## phrase-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.40 (4/10) | 0.60 (6/10) | 0.70 (7/10) | 0.54 |
| table | 0.50 (1/2) | 0.50 (1/2) | 1.00 (2/2) | 0.60 |
| definition | 0.50 (1/2) | 1.00 (2/2) | 1.00 (2/2) | 0.75 |
| prose | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.50 |
| numeric | 0.00 (0/2) | 0.50 (1/2) | 0.50 (1/2) | 0.33 |
| lakh | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.50 |

## Per question (first-hit rank; - = none in top 10)

| id | type | section | strict | phrase | expected | top-3 retrieved sections |
|---|---|---|---|---|---|---|
| h01 | table | 5 | 5 | 5 | 196 | 198; 198; 198,199 |
| h02 | table | 1 | 1 | 1 | 408 | 407; 407,408; 408 |
| h03 | definition | 1 | 1 | 1 | 17 | 16,17; 17; 17 |
| h04 | definition | 1 | 1 | 2 | 129 | 128; 128,129; 129 |
| h05 | prose | 1 | 1 | 1 | 82 | 81,82; 82; 82 |
| h06 | prose | 8 | 8 | - | 267 | 397,398; 398; 398 |
| h07 | numeric | 2 | 2 | 2 | 154 | 127; 127; 127,128 |
| h08 | numeric | 6 | 6 | 6 | 428 | 269,270; 270; 270 |
| h09 | lakh | - | - | - | 186 | 155,156; 156,157; 157,158 |
| h10 | lakh | 1 | 1 | 1 | 58 | 57,58; 58; 58 |
