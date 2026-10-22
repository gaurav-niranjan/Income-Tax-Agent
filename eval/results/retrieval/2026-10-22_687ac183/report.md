# Retrieval eval: 2026-10-22_687ac183

```json
{
  "run_id": "2026-10-22_687ac183",
  "kind": "retrieval",
  "created": "2026-10-22T13:46:50",
  "config_hash": "687ac183",
  "note": "structured chunker",
  "index": "structured-1500__bge-base",
  "mode": "dense",
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
| all | 0.68 (15/22) | 0.91 (20/22) | 0.95 (21/22) | 0.79 |
| table | 0.33 (2/6) | 0.83 (5/6) | 0.83 (5/6) | 0.56 |
| definition | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |
| prose | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |
| numeric | 0.75 (3/4) | 0.75 (3/4) | 1.00 (4/4) | 0.80 |
| lakh | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.83 |

## strict-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.68 (15/22) | 0.91 (20/22) | 0.95 (21/22) | 0.79 |
| table | 0.33 (2/6) | 0.83 (5/6) | 0.83 (5/6) | 0.56 |
| definition | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |
| prose | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |
| numeric | 0.75 (3/4) | 0.75 (3/4) | 1.00 (4/4) | 0.80 |
| lakh | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.83 |

## phrase-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.68 (15/22) | 0.91 (20/22) | 0.95 (21/22) | 0.79 |
| table | 0.33 (2/6) | 0.83 (5/6) | 0.83 (5/6) | 0.56 |
| definition | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |
| prose | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |
| numeric | 0.75 (3/4) | 0.75 (3/4) | 1.00 (4/4) | 0.80 |
| lakh | 0.50 (2/4) | 1.00 (4/4) | 1.00 (4/4) | 0.71 |

## Per question (first-hit rank; - = none in top 10)

| id | type | section | strict | phrase | expected | top-3 retrieved sections |
|---|---|---|---|---|---|---|
| q01 | table | 2 | 2 | 2 | 202 | 2; 2; 2 |
| q02 | table | 1 | 1 | 1 | 393 | 393; 393; 393 |
| q03 | table | 1 | 1 | 1 | 394 | 394; 394; 33 |
| q04 | table | 2 | 2 | 2 | 263 | 352; 352; 352 |
| q05 | table | 3 | 3 | 3 | 19 | 29; 29; 93 |
| q06 | table | - | - | - | 394 | 402; 402; 402 |
| q07 | definition | 1 | 1 | 1 | 2 | 2; 2; 2 |
| q08 | definition | 1 | 1 | 1 | 2 | 2; 2; 2 |
| q09 | definition | 1 | 1 | 1 | 3 | 3; 2; 2 |
| q10 | definition | 2 | 2 | 1 | 2,92 | 515; 515; 2 |
| q11 | prose | 1 | 1 | 1 | 6 | 6; 6; 6 |
| q12 | prose | 1 | 1 | 1 | 1 | 1; 536; 536 |
| q13 | prose | 1 | 1 | 1 | 202 | 202; 202; 333 |
| q14 | prose | 1 | 1 | 1 | 536 | 536; 536; 536 |
| q15 | numeric | 1 | 1 | 1 | 126 | 126; 126; 126 |
| q16 | numeric | 1 | 1 | 1 | 126 | 126; 126; 126 |
| q17 | numeric | 5 | 5 | 5 | 22 | 20; 134; 142 |
| q18 | numeric | 1 | 1 | 1 | 156 | 156; 155; 393 |
| q19 | lakh | 1 | 1 | 1 | 202 | 202; 202; 201 |
| q20 | lakh | 1 | 1 | 1 | 156 | 156; 155; 5 |
| q21 | lakh | 3 | 3 | 3 | 198 | 197; 197; 197 |
| q22 | lakh | 1 | 1 | 2 | 123,Schedule XV | Schedule XV; Schedule XV; 123 |
