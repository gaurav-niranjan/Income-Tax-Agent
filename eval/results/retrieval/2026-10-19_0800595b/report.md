# Retrieval eval: 2026-10-19_0800595b

```json
{
  "run_id": "2026-10-19_0800595b",
  "kind": "retrieval",
  "created": "2026-10-19T14:29:56",
  "config_hash": "0800595b",
  "note": "new fusion",
  "index": "fixed-1000-150-header__bge-base",
  "mode": "hybrid",
  "neighbours": true,
  "depth": 10,
  "strict_share": 0.3,
  "rrf_k": 2,
  "hybrid_candidates": 50,
  "query_prefix": "Represent this sentence for searching relevant passages: ",
  "questions_file": "questions.jsonl",
  "questions_sha": "5826d3f4",
  "n_questions": 22,
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
| all | 0.73 (16/22) | 0.86 (19/22) | 0.86 (19/22) | 0.81 |
| table | 0.67 (4/6) | 0.83 (5/6) | 0.83 (5/6) | 0.77 |
| definition | 0.25 (1/4) | 0.50 (2/4) | 0.50 (2/4) | 0.41 |
| prose | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |
| numeric | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |
| lakh | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |

## strict-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.73 (16/22) | 0.86 (19/22) | 0.86 (19/22) | 0.81 |
| table | 0.67 (4/6) | 0.83 (5/6) | 0.83 (5/6) | 0.77 |
| definition | 0.25 (1/4) | 0.50 (2/4) | 0.50 (2/4) | 0.41 |
| prose | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |
| numeric | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |
| lakh | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |

## phrase-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.50 (11/22) | 0.82 (18/22) | 0.91 (20/22) | 0.66 |
| table | 0.50 (3/6) | 0.67 (4/6) | 0.83 (5/6) | 0.62 |
| definition | 0.25 (1/4) | 0.75 (3/4) | 0.75 (3/4) | 0.50 |
| prose | 0.50 (2/4) | 1.00 (4/4) | 1.00 (4/4) | 0.71 |
| numeric | 0.75 (3/4) | 0.75 (3/4) | 1.00 (4/4) | 0.80 |
| lakh | 0.50 (2/4) | 1.00 (4/4) | 1.00 (4/4) | 0.71 |

## Per question (first-hit rank; - = none in top 10)

| id | type | section | strict | phrase | expected | top-3 retrieved sections |
|---|---|---|---|---|---|---|
| q01 | table | 1 | 1 | 1 | 202 | 201,202; 201,202; 202 |
| q02 | table | 2 | 2 | 2 | 393 | 2; 2; 2 |
| q03 | table | 1 | 1 | 1 | 394 | 393,394; 394; 394 |
| q04 | table | 1 | 1 | 4 | 263 | 262,263; 262,263; 263 |
| q05 | table | 10 | 10 | - | 19 | 201; 201,202; 201,202 |
| q06 | table | 1 | 1 | 1 | 394 | 394; 394; 394 |
| q07 | definition | 1 | 1 | 1 | 2 | 2; 2; 2 |
| q08 | definition | - | - | - | 2 | 393; 393; 393 |
| q09 | definition | 2 | 2 | 2 | 3 | 60; 60; 60,61 |
| q10 | definition | 8 | 8 | 2 | 2,92 | 515; 515; 515 |
| q11 | prose | 1 | 1 | 3 | 6 | 6; 6; 6 |
| q12 | prose | 1 | 1 | 1 | 1 | 1,2; 2; 536 |
| q13 | prose | 1 | 1 | 2 | 202 | 201,202; 201,202; 202 |
| q14 | prose | 1 | 1 | 1 | 536 | 534,535; 535,536; 536 |
| q15 | numeric | 1 | 1 | 1 | 126 | 126; 126; 126 |
| q16 | numeric | 1 | 1 | 1 | 126 | 125,126; 126; 126 |
| q17 | numeric | 2 | 2 | 5 | 22 | 141,142; 142; 142,143 |
| q18 | numeric | 1 | 1 | 1 | 156 | 154,155,156; 155,156; 156,157 |
| q19 | lakh | 1 | 1 | 1 | 202 | 201,202; 201,202; 202 |
| q20 | lakh | 1 | 1 | 1 | 156 | 154,155,156; 155,156; 156,157 |
| q21 | lakh | 1 | 1 | 3 | 198 | 197; 197,198; 198 |
| q22 | lakh | 1 | 1 | 2 | 123,Schedule XV | Schedule XIV; Schedule XIV,Schedule XV; Schedule XV |
