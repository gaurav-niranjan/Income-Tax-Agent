# Retrieval eval: 2026-10-19_f1617416

```json
{
  "run_id": "2026-10-19_f1617416",
  "kind": "retrieval",
  "created": "2026-10-19T14:30:00",
  "config_hash": "f1617416",
  "note": "new fusion",
  "index": "fixed-1000-150-header__bge-base",
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
  "expand_candidates": 10,
  "expand_fusion": "max"
}
```

## section-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.73 (16/22) | 0.95 (21/22) | 1.00 (22/22) | 0.85 |
| table | 0.50 (3/6) | 1.00 (6/6) | 1.00 (6/6) | 0.75 |
| definition | 0.50 (2/4) | 0.75 (3/4) | 1.00 (4/4) | 0.68 |
| prose | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |
| numeric | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |
| lakh | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |

## strict-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.73 (16/22) | 0.95 (21/22) | 1.00 (22/22) | 0.85 |
| table | 0.50 (3/6) | 1.00 (6/6) | 1.00 (6/6) | 0.75 |
| definition | 0.50 (2/4) | 0.75 (3/4) | 1.00 (4/4) | 0.68 |
| prose | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |
| numeric | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |
| lakh | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |

## phrase-hit

| type | hit@1 | hit@3 | hit@5 | mrr |
|---|---|---|---|---|
| all | 0.64 (14/22) | 0.95 (21/22) | 0.95 (21/22) | 0.80 |
| table | 0.50 (3/6) | 0.83 (5/6) | 0.83 (5/6) | 0.67 |
| definition | 0.50 (2/4) | 1.00 (4/4) | 1.00 (4/4) | 0.75 |
| prose | 0.50 (2/4) | 1.00 (4/4) | 1.00 (4/4) | 0.75 |
| numeric | 1.00 (4/4) | 1.00 (4/4) | 1.00 (4/4) | 1.00 |
| lakh | 0.75 (3/4) | 1.00 (4/4) | 1.00 (4/4) | 0.88 |

## Per question (first-hit rank; - = none in top 10)

| id | type | section | strict | phrase | expected | top-3 retrieved sections |
|---|---|---|---|---|---|---|
| q01 | table | 2 | 2 | 2 | 202 | 316,317; 317; 317 |
| q02 | table | 1 | 1 | 1 | 393 | 393; 393; 393 |
| q03 | table | 1 | 1 | 1 | 394 | 393,394; 394; 394 |
| q04 | table | 2 | 2 | - | 263 | 25; 25,26; 26 |
| q05 | table | 2 | 2 | 2 | 19 | 201; 201,202; 201,202 |
| q06 | table | 1 | 1 | 1 | 394 | 394; 394; 394 |
| q07 | definition | 2 | 2 | 2 | 2 | 184; 184; 184 |
| q08 | definition | 1 | 1 | 1 | 2 | 2; 2; 2 |
| q09 | definition | 1 | 1 | 1 | 3 | 2; 2,3,4; 3,4,5 |
| q10 | definition | 5 | 5 | 2 | 2,92 | 515; 515; 515 |
| q11 | prose | 2 | 2 | 2 | 6 | Schedule IV; Schedule IV; Schedule IV |
| q12 | prose | 1 | 1 | 1 | 1 | 1,2; 2; 159 |
| q13 | prose | 1 | 1 | 2 | 202 | 201,202; 201,202; 202 |
| q14 | prose | 1 | 1 | 1 | 536 | 534,535; 535,536; 536 |
| q15 | numeric | 1 | 1 | 1 | 126 | 125,126; 126; 126 |
| q16 | numeric | 1 | 1 | 1 | 126 | 125,126; 126; 126 |
| q17 | numeric | 1 | 1 | 1 | 22 | 21; 21,22; 22 |
| q18 | numeric | 1 | 1 | 1 | 156 | 154,155,156; 155,156; 156,157 |
| q19 | lakh | 1 | 1 | 1 | 202 | 201,202; 201,202; 202 |
| q20 | lakh | 1 | 1 | 1 | 156 | 154,155,156; 155,156; 156,157 |
| q21 | lakh | 1 | 1 | 1 | 198 | 198; 198; 198 |
| q22 | lakh | 1 | 1 | 2 | 123,Schedule XV | Schedule XIV; Schedule XIV,Schedule XV; Schedule XV |

## Expanded queries (the question itself is always searched too)

**q01** What are the income tax rates under the new regime?
- income tax rates total income slab rates individual
- The rates of income tax for the total income of an individual shall be specified in the relevant Finance Act
- What are the income tax rates applicable to the total income of an individual under the default tax regime

**q02** What is the TDS rate when a specified person pays rent for land or a building?
- tax deducted at source rent land building specified person rate
- Where any specified person responsible for paying to a resident any income by way of rent shall deduct tax deducted at source at the rate of
- What is the tax deducted at source rate applicable when a specified person pays rent for land or a building

**q03** At what rate is tax collected at source on the sale of scrap?
- tax collected at source sale of scrap rate
- tax collected at source on the sale of scrap shall be at the rate of
- What is the rate of tax collected at source for the sale of scrap

**q04** What is the due date for filing the income tax return of a salaried person with no business income?
- return of income due date assessee total income without profits and gains of business or profession
- Every person being a resident in India whose total income does not include any profits and gains of business or profession shall furnish a return of income on or before the due date
- What is the due date for furnishing the return of income for an assessee with salary income and no business income

**q05** How much standard deduction can a salaried employee claim under the new tax regime?
- standard deduction salary income under the new tax regime
- Where the total income of an assessee includes income chargeable under the head "Salaries", a deduction of Rs. 75000 shall be allowed
- What is the amount of standard deduction available to a salaried employee for computing total income under the new tax regime

**q06** What is the TCS rate on money sent abroad under the Liberalised Remittance Scheme for education?
- tax collected at source Liberalised Remittance Scheme education
- Where amount is remitted out of India under the Liberalised Remittance Scheme for education, tax collected at source shall be levied at the specified rate
- What is the tax collected at source percentage for amounts remitted abroad under the Liberalised Remittance Scheme for the purpose of education

**q07** Who is included in the definition of a 'person' in the Act?
- person includes individual Hindu undivided family company firm association of persons or body of individuals
- person includes an individual, Hindu undivided family, company, firm, association of persons or body of individuals, local authority, and every other artificial juridical person
- Who falls under the definition of a person for the purposes of the Act

**q08** Who counts as a senior citizen for income tax?
- resident individual of the age of sixty years or more senior citizen
- senior citizen means a resident individual who is of the age of sixty years or more at any time during the tax year
- What is the age limit for a resident individual to be considered a senior citizen for tax purposes

**q09** What does 'tax year' mean?
- tax year definition period
- tax year means the period beginning on the first day of April and ending on the thirty-first day of March
- What is the definition and meaning of the term tax year

**q10** Who is a 'relative' of an individual under the Act?
- relative individual definition spouse child brother sister
- "relative" in relation to an individual means the spouse, brother or sister, or any lineal ascendant or descendant of that individual
- Who is included in the definition of a relative of an individual under the Act

**q11** How many days must an individual stay in India to be treated as a resident?
- resident in India individual stay period days tax year
- An individual shall be resident in India in any tax year if the individual stays in India for a period amounting in all to one hundred and eighty-two days or more
- How many days must an individual stay in India during a tax year to be considered resident in India

**q12** When does the Income-tax Act, 2025 come into force?
- date of commencement of the Income-tax Act 2025
- This Act shall come into force on such date as the Central Government may appoint by notification in the Official Gazette
- When does the Income-tax Act 2025 come into force and apply to the assessee

**q13** Can someone with business income opt out of the new tax regime and later switch back?
- opting out of concessional tax regime business income subsequent tax year
- Where an assessee having income under the head "Profits and gains of business or profession" has exercised the option to pay tax under the concessional rate, such option shall be available for subsequent tax years
- Can an assessee with business income who opted out of the concessional tax regime switch back to it in a later tax year

**q14** What happens to the old Income-tax Act, 1961?
- Income-tax Act 1961 repeal savings provisions
- The Income-tax Act 1961 shall stand repealed and replaced by the Income-tax Act 2025 subject to savings and transitional provisions
- What is the legal effect and repeal status of the former Income-tax Act 1961 under the new tax law

**q15** What is the maximum deduction for health insurance premium paid for parents?
- deduction health insurance premium parents total income
- Where an assessee pays health insurance premium for parents, the deduction allowed from total income shall not exceed Rs. 50000
- What is the maximum deduction allowed under the Act for health insurance premium paid for parents

**q16** How much can be deducted for a preventive health check-up?
- deduction preventive health check-up total income
- Where an assessee incurs expenditure on preventive health check-up, a deduction of up to Rs. 5000 shall be allowed in computing total income
- How much deduction from total income is allowed for expenditure incurred on a preventive health check-up

**q17** What standard deduction is allowed from rental income from a house property?
- income from house property deduction from annual value
- where the income is chargeable under the head "Income from house property", a deduction of a sum equal to thirty percent of the annual value shall be allowed
- what standard deduction is available from the annual value of house property under income from house property

**q18** What is the maximum rebate a resident individual can get under the new tax regime?
- rebate of tax resident individual maximum amount new tax regime
- Where the total income of a resident individual does not exceed Rs. 700000, there shall be allowed a rebate of income-tax of an amount equal to the tax payable on such total income
- What is the maximum tax rebate available to a resident individual under the new tax regime for total income up to Rs. 700000

**q19** What is the tax rate on income between 8 and 12 lakh under the new regime?
- total income rates of tax slab rates
- The rates of income-tax for the total income of a person shall be charged at the specified rates for income exceeding Rs. 800000 up to Rs. 1200000
- What is the tax rate applicable to total income between Rs. 800000 and Rs. 1200000 under the default tax regime

**q20** Is there a tax rebate if my total income is up to 5 lakh?
- rebate of tax total income Rs. 500000
- Where the total income of an assessee does not exceed Rs. 500000, there shall be allowed a rebate of income-tax
- Is a tax rebate available under the Act if the total income of the resident individual is up to Rs. 500000

**q21** At what rate are long-term capital gains on listed shares above 1.25 lakh taxed?
- long-term capital gains listed shares securities transaction tax income tax rate
- Where the total income includes long-term capital gains exceeding Rs. 125000 arising from the transfer of equity shares, the tax payable shall be calculated at the specified rate
- What is the tax rate on long-term capital gains exceeding Rs. 125000 from the transfer of listed shares

**q22** Is the total deduction for life insurance premium and provident fund contributions capped at 1.5 lakh?
- deduction life insurance premium provident fund contribution limit total amount
- Where the gross total income of an assessee includes sums paid towards life insurance premium and provident fund contribution, the aggregate deduction shall not exceed Rs. 150000
- Is the total deduction for life insurance premium and provident fund contributions subject to an upper limit of Rs. 150000

