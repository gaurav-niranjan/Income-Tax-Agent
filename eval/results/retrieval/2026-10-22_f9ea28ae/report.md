# Retrieval eval: 2026-10-22_f9ea28ae

```json
{
  "run_id": "2026-10-22_f9ea28ae",
  "kind": "retrieval",
  "created": "2026-10-22T13:46:50",
  "config_hash": "f9ea28ae",
  "note": "structured chunker",
  "index": "structured-1500__bge-base",
  "mode": "bm25",
  "neighbours": true,
  "depth": 10,
  "strict_share": 0.3,
  "rrf_k": 2,
  "hybrid_candidates": 50,
  "query_prefix": "Represent this sentence for searching relevant passages: ",
  "questions_file": "questions.jsonl",
  "questions_sha": "5826d3f4",
  "n_questions": 22,
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
| all | 0.64 (14/22) | 0.73 (16/22) | 0.77 (17/22) | 0.70 |
| table | 0.83 (5/6) | 0.83 (5/6) | 0.83 (5/6) | 0.86 |
| definition | 0.00 (0/4) | 0.00 (0/4) | 0.00 (0/4) | 0.06 |
| prose | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |
| numeric | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.83 |
| lakh | 0.75 (3/4) | 0.75 (3/4) | 1.00 (4/4) | 0.81 |

## strict-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.64 (14/22) | 0.73 (16/22) | 0.77 (17/22) | 0.70 |
| table | 0.83 (5/6) | 0.83 (5/6) | 0.83 (5/6) | 0.86 |
| definition | 0.00 (0/4) | 0.00 (0/4) | 0.00 (0/4) | 0.06 |
| prose | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |
| numeric | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.83 |
| lakh | 0.75 (3/4) | 0.75 (3/4) | 1.00 (4/4) | 0.81 |

## phrase-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.55 (12/22) | 0.68 (15/22) | 0.77 (17/22) | 0.64 |
| table | 0.67 (4/6) | 0.67 (4/6) | 0.67 (4/6) | 0.69 |
| definition | 0.00 (0/4) | 0.00 (0/4) | 0.25 (1/4) | 0.08 |
| prose | 0.50 (2/4) | 1.00 (4/4) | 1.00 (4/4) | 0.75 |
| numeric | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.83 |
| lakh | 0.75 (3/4) | 0.75 (3/4) | 1.00 (4/4) | 0.81 |

## Per question (first-hit rank; - = none in top 10)

| id | type | section | strict | phrase | expected | top-3 retrieved sections |
|---|---|---|---|---|---|---|
| q01 | table | 1 | 1 | 1 | 202 | 202; 202; 201 |
| q02 | table | 1 | 1 | 1 | 393 | 393; 393; 393 |
| q03 | table | 1 | 1 | 1 | 394 | 394; 394; 393 |
| q04 | table | 1 | 1 | - | 263 | 263; 263; 263 |
| q05 | table | 6 | 6 | 6 | 19 | 202; 202; 202 |
| q06 | table | 1 | 1 | 1 | 394 | 394; 394; 402 |
| q07 | definition | - | - | - | 2 | Schedule III; Schedule III; Schedule IV |
| q08 | definition | 8 | 8 | 8 | 2 | 153; 153; 263 |
| q09 | definition | - | - | - | 3 | 82; 82; 60 |
| q10 | definition | 9 | 9 | 5 | 2,92 | 515; 515; 515 |
| q11 | prose | 1 | 1 | 1 | 6 | 6; 6; Schedule IV |
| q12 | prose | 1 | 1 | 1 | 1 | 1; 411; 411 |
| q13 | prose | 1 | 1 | 2 | 202 | 202; 202; 202 |
| q14 | prose | 2 | 2 | 2 | 536 | 531; 536; 536 |
| q15 | numeric | 1 | 1 | 1 | 126 | 126; 126; 126 |
| q16 | numeric | 1 | 1 | 1 | 126 | 126; 126; 126 |
| q17 | numeric | 3 | 3 | 3 | 22 | 23; 130; 130 |
| q18 | numeric | 1 | 1 | 1 | 156 | 156; 198; 198 |
| q19 | lakh | 1 | 1 | 1 | 202 | 202; 202; 393 |
| q20 | lakh | 1 | 1 | 1 | 156 | 156; 155; 62 |
| q21 | lakh | 4 | 4 | 4 | 198 | 197; 197; 69 |
| q22 | lakh | 1 | 1 | 1 | 123,Schedule XV | 123; Schedule XV; Schedule XV |
