# Retrieval eval: 2026-10-24_cf10af4d

```json
{
  "run_id": "2026-10-24_cf10af4d",
  "kind": "retrieval",
  "created": "2026-10-24T15:25:46",
  "config_hash": "cf10af4d",
  "note": "grid",
  "index": "structured-1500__bge-base",
  "mode": "dense",
  "neighbours": true,
  "depth": 10,
  "strict_share": 0.3,
  "rrf_k": 2,
  "hybrid_candidates": 50,
  "query_prefix": "Represent this sentence for searching relevant passages: ",
  "questions_file": "heldout.jsonl",
  "questions_sha": "39d7c570",
  "n_questions": 10,
  "git_commit": "78254c5",
  "index_manifest": {
    "name": "structured-1500__bge-base",
    "created": "2026-10-22T08:16:32+00:00",
    "source": {
      "pdf": "Income-tax-Act-2025_2026_2026-08-25_10-41-45_a1d3cd_en.pdf",
      "pages_sha256": "d040fa5f9591e338",
      "n_pages": 674
    },
    "cleaning": {
      "strip_footnotes": true
    },
    "chunker": {
      "type": "structured",
      "max_chars": 1500,
      "min_chars": 300,
      "size_measure": "characters, whitespace runs collapsed",
      "search_prefix": "section + sub-section/table-row label + title (dense + bm25)"
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
      "n_chunks": 1683,
      "n_chunks_multi_section": 0,
      "chars_total": 1678896,
      "tokens": {
        "min": 20,
        "p50": 256,
        "p90": 343,
        "p99": 393,
        "max": 437,
        "mean": 231.4,
        "over_512": 0
      },
      "embed_seconds": 231.1
    }
  },
  "rerank": true,
  "rerank_model": "Xenova/ms-marco-MiniLM-L-6-v2",
  "rerank_candidates": 20,
  "rerank_rewrite_weight": 0.5
}
```

## section-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.80 (8/10) | 0.90 (9/10) | 0.90 (9/10) | 0.83 |
| table | 0.50 (1/2) | 1.00 (2/2) | 1.00 (2/2) | 0.67 |
| definition | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| prose | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| numeric | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| lakh | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.50 |

## strict-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.80 (8/10) | 0.90 (9/10) | 0.90 (9/10) | 0.83 |
| table | 0.50 (1/2) | 1.00 (2/2) | 1.00 (2/2) | 0.67 |
| definition | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| prose | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| numeric | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| lakh | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.50 |

## phrase-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.80 (8/10) | 0.90 (9/10) | 0.90 (9/10) | 0.83 |
| table | 0.50 (1/2) | 1.00 (2/2) | 1.00 (2/2) | 0.67 |
| definition | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| prose | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| numeric | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| lakh | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.50 |

## Per question (first-hit rank; - = none in top 10)

| id | type | section | strict | phrase | expected | top-3 retrieved sections |
|---|---|---|---|---|---|---|
| h01 | table | 3 | 3 | 3 | 196 | 198; 198; 69 |
| h02 | table | 1 | 1 | 1 | 408 | 408; 424; 424 |
| h03 | definition | 1 | 1 | 1 | 17 | 17; 17; Schedule III |
| h04 | definition | 1 | 1 | 1 | 129 | 129; 129; 131 |
| h05 | prose | 1 | 1 | 1 | 82 | 82; 82; 82 |
| h06 | prose | 1 | 1 | 1 | 267 | 267; 267; 267 |
| h07 | numeric | 1 | 1 | 1 | 154 | 154; 127; 127 |
| h08 | numeric | 1 | 1 | 1 | 428 | 428; 423; 423 |
| h09 | lakh | - | - | - | 186 | 70; 70; 70 |
| h10 | lakh | 1 | 1 | 1 | 58 | 58; 58; 58 |
