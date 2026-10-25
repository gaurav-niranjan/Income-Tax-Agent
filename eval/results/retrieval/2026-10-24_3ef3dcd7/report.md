# Retrieval eval: 2026-10-24_3ef3dcd7

```json
{
  "run_id": "2026-10-24_3ef3dcd7",
  "kind": "retrieval",
  "created": "2026-10-24T15:25:17",
  "config_hash": "3ef3dcd7",
  "note": "grid",
  "index": "structured-1500__bge-base",
  "mode": "dense",
  "neighbours": true,
  "depth": 10,
  "strict_share": 0.3,
  "rrf_k": 2,
  "hybrid_candidates": 50,
  "query_prefix": "Represent this sentence for searching relevant passages: ",
  "questions_file": "questions.jsonl",
  "questions_sha": "9fc4b4a2",
  "n_questions": 23,
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
| all | 0.91 (21/23) | 0.96 (22/23) | 0.96 (22/23) | 0.93 |
| table | 0.83 (5/6) | 0.83 (5/6) | 0.83 (5/6) | 0.83 |
| definition | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |
| prose | 1.00 (5/5) | 1.00 (5/5) | 1.00 (5/5) | 1.00 |
| numeric | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |
| lakh | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |

## strict-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.91 (21/23) | 0.96 (22/23) | 0.96 (22/23) | 0.93 |
| table | 0.83 (5/6) | 0.83 (5/6) | 0.83 (5/6) | 0.83 |
| definition | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |
| prose | 1.00 (5/5) | 1.00 (5/5) | 1.00 (5/5) | 1.00 |
| numeric | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |
| lakh | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |

## phrase-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.83 (19/23) | 0.91 (21/23) | 0.91 (21/23) | 0.87 |
| table | 0.67 (4/6) | 0.83 (5/6) | 0.83 (5/6) | 0.75 |
| definition | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |
| prose | 0.80 (4/5) | 0.80 (4/5) | 0.80 (4/5) | 0.80 |
| numeric | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |
| lakh | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |

## Per question (first-hit rank; - = none in top 10)

| id | type | section | strict | phrase | expected | top-3 retrieved sections |
|---|---|---|---|---|---|---|
| q01 | table | 1 | 1 | 1 | 202 | 202; 202; 202 |
| q02 | table | 1 | 1 | 1 | 393 | 393; 393; 393 |
| q03 | table | 1 | 1 | 1 | 394 | 394; 394; 394 |
| q04 | table | 1 | 1 | 2 | 263 | 263; 263; 263 |
| q05 | table | 1 | 1 | 1 | 19 | 19; 19; 146 |
| q06 | table | - | - | - | 394 | 402; 402; 402 |
| q07 | definition | 1 | 1 | 1 | 2 | 2; 2; 2 |
| q08 | definition | 2 | 2 | 2 | 2 | 402; 402; 402 |
| q09 | definition | 1 | 1 | 1 | 3 | 3; 143; 143 |
| q10 | definition | 1 | 1 | 1 | 2,92 | 2; 2; 2 |
| q11 | prose | 1 | 1 | 1 | 6 | 6; 6; 6 |
| q12 | prose | 1 | 1 | 1 | 1 | 1; 536; 536 |
| q13 | prose | 1 | 1 | 1 | 202 | 202; 202; 320 |
| q14 | prose | 1 | 1 | 1 | 536 | 536; 536; 531 |
| q15 | numeric | 1 | 1 | 1 | 126 | 126; 126; 126 |
| q16 | numeric | 1 | 1 | 1 | 126 | 126; 126; 126 |
| q17 | numeric | 1 | 1 | 1 | 22 | 22; 22; 130 |
| q18 | numeric | 1 | 1 | 1 | 156 | 156; 154; 202 |
| q19 | lakh | 1 | 1 | 1 | 202 | 202; 202; 202 |
| q20 | lakh | 1 | 1 | 1 | 156 | 156; 155; 393 |
| q21 | lakh | 1 | 1 | 1 | 198 | 198; 198; 197 |
| q22 | lakh | 1 | 1 | 1 | 123,Schedule XV | 123; Schedule XV; Schedule XV |
| q27 | prose | 1 | 1 | - | 212,213,214,215,216,217 | 216; 160; 160 |
