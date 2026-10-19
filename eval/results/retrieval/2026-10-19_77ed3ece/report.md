# Retrieval eval: 2026-10-19_77ed3ece

```json
{
  "run_id": "2026-10-19_77ed3ece",
  "kind": "retrieval",
  "created": "2026-10-19T12:55:33",
  "config_hash": "77ed3ece",
  "note": "held-out, query expansion",
  "index": "fixed-1000-150-header__bge-base",
  "mode": "hybrid",
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
  },
  "expand": true,
  "expand_model": "gemini-3.5-flash-lite",
  "expand_prompt_sha": "de9cc1d3",
  "expand_candidates": 20
}
```

## section-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.80 (8/10) | 0.90 (9/10) | 0.90 (9/10) | 0.85 |
| table | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| definition | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| prose | 0.50 (1/2) | 1.00 (2/2) | 1.00 (2/2) | 0.75 |
| numeric | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| lakh | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.50 |

## strict-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.80 (8/10) | 0.90 (9/10) | 0.90 (9/10) | 0.85 |
| table | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| definition | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| prose | 0.50 (1/2) | 1.00 (2/2) | 1.00 (2/2) | 0.75 |
| numeric | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| lakh | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.50 |

## phrase-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.70 (7/10) | 0.90 (9/10) | 0.90 (9/10) | 0.80 |
| table | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| definition | 1.00 (2/2) | 1.00 (2/2) | 1.00 (2/2) | 1.00 |
| prose | 0.50 (1/2) | 1.00 (2/2) | 1.00 (2/2) | 0.75 |
| numeric | 0.50 (1/2) | 1.00 (2/2) | 1.00 (2/2) | 0.75 |
| lakh | 0.50 (1/2) | 0.50 (1/2) | 0.50 (1/2) | 0.50 |

## Per question (first-hit rank; - = none in top 10)

| id | type | section | strict | phrase | expected | top-3 retrieved sections |
|---|---|---|---|---|---|---|
| h01 | table | 1 | 1 | 1 | 196 | 196; 196,197; 197 |
| h02 | table | 1 | 1 | 1 | 408 | 407; 407,408; 408 |
| h03 | definition | 1 | 1 | 1 | 17 | 16,17; 17; 17 |
| h04 | definition | 1 | 1 | 1 | 129 | 129; 129,130; 129,130 |
| h05 | prose | 2 | 2 | 2 | 82 | 86; 86; 86 |
| h06 | prose | 1 | 1 | 1 | 267 | 267; 267; 267 |
| h07 | numeric | 1 | 1 | 2 | 154 | 154; 154,155,156; 155,156 |
| h08 | numeric | 1 | 1 | 1 | 428 | 427,428; 428; 428,429 |
| h09 | lakh | - | - | - | 186 | 393; 393; 393 |
| h10 | lakh | 1 | 1 | 1 | 58 | 57,58; 58; 58 |

## Expanded queries (the question itself is always searched too)

**h01** What is the tax rate on STCG from selling equity shares on the stock exchange?
- short term capital gains equity shares recognized stock exchange tax rate
- Where the total income of an assessee includes any short term capital gains arising from the transfer of an equity share in a company where such transaction is chargeable to securities transaction tax
- What is the tax rate on short term capital gains from selling equity shares on a recognized stock exchange

**h02** By which dates do I have to pay advance tax, and how much each time?
- advance tax instalment due dates amount payable
- Where advance tax is payable by an assessee, the instalment and due date shall be calculated as a specified percentage of the total tax liability
- What are the due dates and the required percentage amounts for paying advance tax installments during the tax year

**h03** Is free housing given by my employer taxed as a perk?
- perquisite value of residential accommodation provided by employer
- Where rent-free accommodation is provided to the assessee by the employer, the value of the perquisite shall be computed in the prescribed manner
- How is the value of residential accommodation provided free of cost by an employer determined for taxation as a perquisite in the hands of the employee

**h04** What counts as 'higher education' for the education loan interest deduction?
- interest deduction loan higher education course of study
- where an assessee has taken a loan for higher education the deduction shall be allowed for interest paid on such loan
- what definition or courses qualify as higher education for claiming a deduction for interest paid on a loan

**h05** Like the old section 54, can I avoid capital gains tax on selling my house if I buy another one?
- capital gains on transfer of residential house property investment in another residential house
- Where capital gains arise from the transfer of a residential house property, the assessee shall be exempt from tax to the extent of investment in another residential house
- Can capital gains tax be avoided upon selling a residential house by purchasing another residential house property

**h06** How much extra tax do I pay if I file an ITR-U to correct an old return?
- updated tax return additional tax payable return of income furnished
- Where an updated return of income is furnished by an assessee, an additional tax shall be payable calculated at the rate of twenty percent or fifty percent of the aggregate of tax and interest due
- How is the additional tax calculated when an assessee files an updated return of income to correct a previous return for a tax year

**h07** How much deduction can a person with severe disability claim?
- deduction person with severe disability total income
- Where an assessee, being a resident in India, is a person with severe disability, there shall be allowed a deduction of Rs. 125000 in computing total income
- What is the maximum deduction allowed from total income for an assessee who is a person with severe disability

**h08** What is the late fee for filing an income tax return after the due date?
- fee for default in furnishing return of income after due date
- Where a person fails to furnish a return of income within the due date, such person shall pay a fee of Rs. 5000
- What is the late fee payable by an assessee for filing the return of income after the due date specified

**h09** Can I accept 3 lakh in cash when I sell my car?
- repayable amount advance sum in cash immovable property transfer limit
- No person shall receive an amount of Rs. 200000 or more in cash in relation to transfer of any asset
- Can an assessee accept cash of Rs. 300000 for the sale of a motor car

**h10** Can my shop with a turnover of 2.5 crore use the presumptive tax scheme?
- profits and gains of business or profession presumptive taxation turnover Rs. 25000000
- where the total turnover or gross receipts of an eligible business does not exceed Rs. 25000000, a sum equal to eight percent of the total turnover shall be deemed to be the profits and gains of such business
- can an assessee engaged in business with a total turnover of Rs. 25000000 opt for the presumptive taxation scheme for determining total income

