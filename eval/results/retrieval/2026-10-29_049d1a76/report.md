# Retrieval eval: 2026-10-29_049d1a76

```json
{
  "run_id": "2026-10-29_049d1a76",
  "kind": "retrieval",
  "created": "2026-10-29T17:21:56",
  "config_hash": "049d1a76",
  "note": "Ladder 2: + section title",
  "index": "fixed-1000-150-header__bge-base",
  "mode": "dense",
  "neighbours": false,
  "depth": 10,
  "strict_share": 0.3,
  "rrf_k": 2,
  "hybrid_candidates": 50,
  "query_prefix": "Represent this sentence for searching relevant passages: ",
  "questions_file": "questions.jsonl",
  "questions_sha": "502ed3c5",
  "n_questions": 26,
  "git_commit": "729e6b5",
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
| all | 0.62 (16/26) | 0.77 (20/26) | 0.85 (22/26) | 0.70 |
| table | 0.57 (4/7) | 0.71 (5/7) | 0.86 (6/7) | 0.68 |
| definition | 0.40 (2/5) | 0.40 (2/5) | 0.60 (3/5) | 0.45 |
| prose | 0.60 (3/5) | 0.80 (4/5) | 0.80 (4/5) | 0.70 |
| numeric | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.83 |
| lakh | 0.80 (4/5) | 1.00 (5/5) | 1.00 (5/5) | 0.87 |

## strict-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.62 (16/26) | 0.77 (20/26) | 0.85 (22/26) | 0.70 |
| table | 0.57 (4/7) | 0.71 (5/7) | 0.86 (6/7) | 0.68 |
| definition | 0.40 (2/5) | 0.40 (2/5) | 0.60 (3/5) | 0.45 |
| prose | 0.60 (3/5) | 0.80 (4/5) | 0.80 (4/5) | 0.70 |
| numeric | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.83 |
| lakh | 0.80 (4/5) | 1.00 (5/5) | 1.00 (5/5) | 0.87 |

## phrase-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.50 (13/26) | 0.73 (19/26) | 0.73 (19/26) | 0.60 |
| table | 0.43 (3/7) | 0.43 (3/7) | 0.43 (3/7) | 0.45 |
| definition | 0.60 (3/5) | 0.60 (3/5) | 0.60 (3/5) | 0.60 |
| prose | 0.40 (2/5) | 0.80 (4/5) | 0.80 (4/5) | 0.57 |
| numeric | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.83 |
| lakh | 0.40 (2/5) | 1.00 (5/5) | 1.00 (5/5) | 0.63 |

## Per question (first-hit rank; - = none in top 10)

| id | type | section | strict | phrase | expected | top-3 retrieved sections |
|---|---|---|---|---|---|---|
| q01 | table | 1 | 1 | 1 | 202 | 202; 201,202; 333,334 |
| q02 | table | 1 | 1 | 1 | 393 | 393; 2; 397 |
| q03 | table | 1 | 1 | 1 | 394 | 394; 394; 394 |
| q04 | table | 1 | 1 | - | 263 | 263; 263; 352 |
| q05 | table | 4 | 4 | - | 19 | 28,29; 146; 146 |
| q06 | table | 7 | 7 | 7 | 394 | 193; 207,208; 208,209 |
| q07 | definition | 1 | 1 | 1 | 2 | 2; 355; 127 |
| q08 | definition | - | - | - | 2 | 402; 393; 393 |
| q09 | definition | 1 | 1 | 1 | 3 | 2,3,4; 3,4,5; 2 |
| q10 | definition | 4 | 4 | 1 | 2,92 | 355; 355; 515,516 |
| q11 | prose | 1 | 1 | 3 | 6 | 6; 6; 5,6 |
| q12 | prose | 1 | 1 | 1 | 1 | 1,2; 536; 201 |
| q13 | prose | 2 | 2 | 2 | 202 | 319,320; 202; 333,334 |
| q14 | prose | 1 | 1 | 1 | 536 | 535,536; 536; 536 |
| q15 | numeric | 1 | 1 | 1 | 126 | 126; 126; 126 |
| q16 | numeric | 1 | 1 | 1 | 126 | 126; 126; 126 |
| q17 | numeric | 3 | 3 | 3 | 22 | 142; 134; 22 |
| q18 | numeric | 1 | 1 | 1 | 156 | 155,156; 154,155,156; 156,157 |
| q19 | lakh | 1 | 1 | 1 | 202 | 202; 201,202; 202 |
| q20 | lakh | 1 | 1 | 2 | 156 | 156,157; 155,156; 393 |
| q21 | lakh | 3 | 3 | 3 | 198 | 197; 214,215; 198 |
| q22 | lakh | 1 | 1 | 3 | 123,Schedule XV | Schedule XV; Schedule XV; 122,123,124 |
| q27 | prose | - | - | - | 212,213,214,215,216,217 | 9; 211; 5,6 |
| q28 | table | 3 | 3 | - | 194 | 445,446; 446,447,448; 194,195 |
| q29 | lakh | 1 | 1 | 1 | 109,202 | 109,110; 110,111; 86 |
| q30 | definition | - | - | - | 2 | 197,198; 198; 69 |
