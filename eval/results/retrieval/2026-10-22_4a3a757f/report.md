# Retrieval eval: 2026-10-22_4a3a757f

```json
{
  "run_id": "2026-10-22_4a3a757f",
  "kind": "retrieval",
  "created": "2026-10-22T13:46:52",
  "config_hash": "4a3a757f",
  "note": "held-out, structured chunker",
  "index": "structured-1500__bge-base",
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
  "git_commit": "ebc048c",
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
  }
}
```

## section-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.50 (5/10) | 0.60 (6/10) | 0.60 (6/10) | 0.57 |
| table | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.50 |
| definition | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| prose | 0.00 (0/2) | 0.50 (1/2) | 0.50 (1/2) | 0.33 |
| numeric | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.50 |
| lakh | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.50 |

## strict-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.50 (5/10) | 0.60 (6/10) | 0.60 (6/10) | 0.57 |
| table | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.50 |
| definition | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| prose | 0.00 (0/2) | 0.50 (1/2) | 0.50 (1/2) | 0.33 |
| numeric | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.50 |
| lakh | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.50 |

## phrase-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.50 (5/10) | 0.60 (6/10) | 0.60 (6/10) | 0.55 |
| table | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.50 |
| definition | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| prose | 0.00 (0/2) | 0.50 (1/2) | 0.50 (1/2) | 0.25 |
| numeric | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.50 |
| lakh | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.50 |

## Per question (first-hit rank; - = none in top 10)

| id | type | section | strict | phrase | expected | top-3 retrieved sections |
|---|---|---|---|---|---|---|
| h01 | table | - | - | - | 196 | 198; 198; 90 |
| h02 | table | 1 | 1 | 1 | 408 | 408; 407; 407 |
| h03 | definition | 1 | 1 | 1 | 17 | 17; 17; 158 |
| h04 | definition | 1 | 1 | 1 | 129 | 129; 129; 394 |
| h05 | prose | 2 | 2 | 2 | 82 | 86; 86; 86 |
| h06 | prose | 6 | 6 | - | 267 | 428; 456; 398 |
| h07 | numeric | 1 | 1 | 1 | 154 | 154; 127; 127 |
| h08 | numeric | - | - | - | 428 | 270; 270; 423 |
| h09 | lakh | - | - | - | 186 | 319; 393; 393 |
| h10 | lakh | 1 | 1 | 1 | 58 | 58; 58; 58 |
