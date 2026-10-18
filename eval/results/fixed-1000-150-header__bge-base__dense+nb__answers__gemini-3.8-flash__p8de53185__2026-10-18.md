# Answer eval: fixed-1000-150-header__bge-base__dense+nb__answers__gemini-3.8-flash__2026-10-18

```json
{
  "index": "fixed-1000-150-header__bge-base",
  "mode": "dense",
  "neighbours": true,
  "k": 5,
  "answer_model": "gemini-3.5-flash-lite",
  "judge_model": "gemini-3.8-flash",
  "prompts_sha256": "8de531856422",
  "questions_file": "questions.jsonl",
  "n_questions": 26,
  "n_answered": 26,
  "git_commit": "59f6cec",
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

| metric | value |
|---|---|
| correct (in scope) | 0.00 (0/0) |
| correct or partial (in scope) | 0.00 (0/0) |
| faithful (all) | 0.00 (0/0) |
| refused, out of scope | 0.00 (0/0) |
| refused, in scope (false refusals) | 0.00 (0/0) |
| unjudged | 26 |

| type | correct | partial | incorrect |
|---|---|---|---|

## Every answer

### q01 (table): UNJUDGED, faithful=None, refused=None
**Q:** What are the income tax rates under the new regime?

**Reference:** Nil up to Rs. 4,00,000; 5% from Rs. 4,00,001 to 8,00,000; 10% to 12,00,000; 15% to 16,00,000; 20% to 20,00,000; 25% to 24,00,000; 30% above Rs. 24,00,000 (Section 202(1) Table).

**Answer:**

The income tax rates under the new regime for individuals, Hindu undivided families, and others are:

* **Upto Rs. 400000 (4 lakh):** Nil [Section 202]
* **From Rs. 400001 to Rs. 800000 (8 lakh):** 5% [Section 202]
* **From Rs. 800001 to Rs. 1200000 (12 lakh):** 10% [Section 202]
* **From Rs. 1200001 to Rs. 1600000 (16 lakh):** 15% [Section 202]
* **From Rs. 1600001 to Rs. 2000000 (20 lakh):** 20% [Section 202]
* **From Rs. 2000001 to Rs. 2400000 (24 lakh):** 25% [Section 202]
* **Above Rs. 2400000 (24 lakh):** 30% [Section 202]

**Key Conditions:**
* This applies to individuals, Hindu undivided families, associations of persons (other than co-operative societies), bodies of individuals (whether incorporated or not), and artificial juridical persons referred to in section 2(77)(g) [Section 202].
* It applies unless the person exercises an option not to be taxed under this regime in the manner provided under sub-section (4) [Section 202].
* The total income must be computed without specified exemptions, deductions, allowances, perquisites, and without certain loss set-offs (such as losses from house property against other income or losses/depreciation tied to disallowed deductions) as detailed in section 202(2) [Section 202].

**Retrieved sections:** 201,202; 202; 202; 201,202; 332,333; 333,334; 334,335; 201; 202; 202,203

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q02 (table): UNJUDGED, faithful=None, refused=None
**Q:** What is the TDS rate when a specified person pays rent for land or a building?

**Reference:** 10% for land, building, furniture or fittings (2% for machinery, plant or equipment). Threshold: Rs. 50,000 for a month or part of a month (Section 393(1) Table, Sl. No. 2(ii)).

**Answer:**

The TDS rate is 10% [Section 393]. 

**Key Conditions:**
* It applies specifically to the use of any land, or building (including factory building), or land appurtenant to a building (including factory building), or furniture, or fittings [Section 393].
* The threshold limit must exceed Rs. 50,000 for a month or part of a month [Section 393].

**Retrieved sections:** 393; 393; 393; 2; 2; 2; 397; 397; 397; 393; 19; 19,20; 20,21

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q03 (table): UNJUDGED, faithful=None, refused=None
**Q:** At what rate is tax collected at source on the sale of scrap?

**Reference:** 2%, collected by the seller (Section 394(1) Table, Sl. No. 4).

**Answer:**

Tax is collected at source on the sale of scrap at the rate of 2% [Section 394].

**Retrieved sections:** 393,394; 394; 394; 394; 394; 394,395; 33; 33; 33; 33

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q04 (table): UNJUDGED, faithful=None, refused=None
**Q:** What is the due date for filing the income tax return of a salaried person with no business income?

**Reference:** 31st July of the financial year after the tax year ("Any other assessee", Section 263(1)(c) Table, Sl. No. 4).

**Answer:**

The due date for filing the income tax return of any other assessee (such as a salaried person with no business income) is 31st July of the financial year succeeding the relevant tax year [Section 263, Table item 4].

**Retrieved sections:** 263; 263; 263; 263; 263; 263; 352; 352; 352; 423; 423; 423; 295; 295; 295

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q05 (table): UNJUDGED, faithful=None, refused=None
**Q:** How much standard deduction can a salaried employee claim under the new tax regime?

**Reference:** Rs. 75,000 or the salary, whichever is less, when tax is computed under the new regime (section 202(1)); Rs. 50,000 or the salary in any other case (Section 19(1) Table, Sl. No. 2).

**Answer:**

I could not find this in the Act.

**Retrieved sections:** 28,29; 28,29; 29; 146; 146; 146; 144,145,146; 146; 19; 19; 19; 392; 392; 392

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q06 (table): UNJUDGED, faithful=None, refused=None
**Q:** What is the TCS rate on money sent abroad under the Liberalised Remittance Scheme for education?

**Reference:** 2% for education or medical treatment, and 20% for other purposes, on amounts above ten lakh rupees, collected by the authorised dealer (Section 394(1) Table, Sl. No. 7).

**Answer:**

I could not find this in the Act.

**Retrieved sections:** 191,192,193; 193; 193; 207,208; 207,208; 208; 208,209; 208,209; 209; 209; 209,210; 210; 209

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q07 (definition): UNJUDGED, faithful=None, refused=None
**Q:** Who is included in the definition of a 'person' in the Act?

**Reference:** An individual, a Hindu undivided family, a company, a firm, an association of persons or body of individuals, a local authority, and every other artificial juridical person (Section 2(77)).

**Answer:**

A "person" includes:
* An individual [Section 2]
* A Hindu undivided family [Section 2]
* A company [Section 2]
* A firm [Section 2]
* An association of persons or a body of individuals, whether incorporated or not [Section 2]
* A local authority [Section 2]
* Every artificial juridical person, not falling within any of the preceding sub-clauses (whether or not such an association of persons, body of individuals, local authority, or artificial juridical person was formed, established, or incorporated with the object of deriving income, profits, or gains) [Section 2].

**Retrieved sections:** 2; 2; 2; 355; 355; 355,356; 127; 127; 127,128; 317,318; 318,319; 318,319; 2

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q08 (definition): UNJUDGED, faithful=None, refused=None
**Q:** Who counts as a senior citizen for income tax?

**Reference:** An individual resident in India who is 60 years or older at any time during the tax year (Section 2(100)).

**Answer:**

I could not find this in the Act.

**Retrieved sections:** 402; 402; 402; 393; 393; 393; 393; 393; 393; 393; 3,4,5; 4,5; 5,6

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q09 (definition): UNJUDGED, faithful=None, refused=None
**Q:** What does 'tax year' mean?

**Reference:** The 12-month financial year starting on 1st April. For a new business or new source of income, it runs from the start date to the end of that financial year (Section 3).

**Answer:**

"Tax year" means the twelve months period of the financial year commencing on the 1st April [Section 3(1)].

**Key conditions:**
* For a business or profession newly set up, or a source of income newly coming into existence in any financial year, the tax year is the period beginning with the date of setting up of such business or profession, or the date on which such source of income newly comes into existence, and ending with that financial year [Section 3(2)].

**Retrieved sections:** 2; 2,3,4; 3,4,5; 4,5; 2; 2; 2; 143; 143,144; 144; 332; 332; 332

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q10 (definition): UNJUDGED, faithful=None, refused=None
**Q:** Who is a 'relative' of an individual under the Act?

**Reference:** Generally: the husband, wife, brother, sister, or any lineal ascendant or descendant (maternal and paternal) of the individual (Section 2(94)). For gifts, Section 92(5)(g) gives a wider list.

**Answer:**

Under Section 92 of the Act, in the case of an individual, "relative" means:
* Spouse [Section 92]
* Brother or sister [Section 92]
* Brother or sister of the spouse [Section 92]
* Brother or sister of either of the parents [Section 92]
* Any lineal ascendant (maternal as well as paternal) or descendant [Section 92]
* Any lineal ascendant (maternal as well as paternal) or descendant of the spouse [Section 92]
* Spouse of the persons referred to in the brother, sister, lineal ascendant, or descendant categories above [Section 92].

*(Note: The Act provides different definitions of "relative" for other specific contexts, such as interpretation under Section 355 or appearance by an authorised representative under Section 515, which apply only for those specific purposes.)*

**Retrieved sections:** 355; 355; 355; 355; 515; 515,516; 516,517,518,519; 92; 92,93; 93; 99; 99; 99,100

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q11 (prose): UNJUDGED, faithful=None, refused=None
**Q:** How many days must an individual stay in India to be treated as a resident?

**Reference:** 182 days or more in the tax year, or 60 days in the year plus 365 days in total over the previous four years (Section 6(2)), with exceptions in 6(3) to 6(5).

**Answer:**

An individual shall be resident in India in a tax year if they meet either of the following conditions:

* They are in India for a total period of 182 days or more in that tax year [Section 6].
* They are in India cumulatively for 60 days or more during that year and have been in India cumulatively for 365 days or more in the four years preceding such tax year [Section 6]. 

However, for a citizen of India or a person of Indian origin who, being outside India, comes on a visit to India and has a total income exceeding fifteen lakh rupees (excluding income from foreign sources) during the tax year, the 60-day period in the second condition is replaced with 120 days [Section 6]. Furthermore, the second condition does not apply to a citizen of India who leaves India in any tax year as a member of the crew of an Indian ship or for the purposes of employment outside India [Section 6].

**Retrieved sections:** 6; 6; 6,7; 6; 6; 5,6; 5,6; 7,8

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q12 (prose): UNJUDGED, faithful=None, refused=None
**Q:** When does the Income-tax Act, 2025 come into force?

**Reference:** On 1st April, 2026, unless the Act says otherwise for a provision (Section 1(3)).

**Answer:**

The Income-tax Act, 2025 comes into force on the 1st April, 2026, save as otherwise provided in the Act [Section 1(3)].

**Retrieved sections:** 1,2; 2; 536; 536; 536; 200,201; 201; 201; 536; 536; 536; 536

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q13 (prose): UNJUDGED, faithful=None, refused=None
**Q:** Can someone with business income opt out of the new tax regime and later switch back?

**Reference:** Yes, once. They opt out by the return due date; the choice then applies to later years; it can be withdrawn only once; after that they can never opt out again, unless they stop having business income (Section 202(4)(a)).

**Answer:**

No. After withdrawing the option for a tax year, a person having income from business or profession shall never be eligible to exercise the option again, except where such person ceases to have any income from business or profession [Section 202(4)(a)(iv)].

**Retrieved sections:** 318,319; 319,320; 320; 202; 202; 202,203; 332,333; 333,334; 334,335; 352; 352; 352; 203

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q14 (prose): UNJUDGED, faithful=None, refused=None
**Q:** What happens to the old Income-tax Act, 1961?

**Reference:** It is repealed, but past actions, rights and liabilities, and pending proceedings under it are saved (Section 536).

**Answer:**

The Income-tax Act, 1961 is repealed [Section 536]. 

Key conditions and rules associated with the repeal:
* Previous operations, orders, rights, privileges, obligations, and liabilities acquired, accrued, or incurred under the repealed Act are generally unaffected [Section 536].
* The provisions of the repealed Act continue to apply to any pending proceedings on the commencement date of the Act and to any proceedings initiated on or after April 1, 2026, for any tax year beginning before April 1, 2026 [Section 536].

**Retrieved sections:** 534,535; 535,536; 536; 536; 536; 536; 536; 536; 536; 536; 536

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q15 (numeric): UNJUDGED, faithful=None, refused=None
**Q:** What is the maximum deduction for health insurance premium paid for parents?

**Reference:** Rs. 25,000, or Rs. 50,000 if the parent is a senior citizen. Together with medical expenditure for parents, the total is capped at Rs. 50,000 (Section 126(2)(b), (4), (8)).

**Answer:**

Yes, the maximum deduction for health insurance premium paid for the parent or parents of the assessee is Rs. 25000 (25 thousand) in aggregate, which can include any payment made for preventive health check-up [Section 126]. 

**Key conditions:**
* If the parent is a senior citizen, the limit of Rs. 25000 (25 thousand) is substituted with Rs. 50000 (50 thousand) [Section 126].
* For a senior citizen, if a deduction is claimed for medical expenditure incurred on their health, no amount must have been paid to effect or keep in force their health insurance [Section 126].
* The payment must be made by a mode other than cash (except for preventive health check-up payments, which can be in cash) [Section 126].
* If the sum is paid in a lump sum for more than a year, the deduction is allowed for each relevant tax year equal to the appropriate fraction of such amount [Section 126].
* The health insurance must be as per a scheme made by the General Insurance Corporation of India and approved by the Central Government, or by any other insurer approved by the Insurance Regulatory and Development Authority [Section 126].

**Retrieved sections:** 126; 126; 126; 126; 125,126; 125; 126,127

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q16 (numeric): UNJUDGED, faithful=None, refused=None
**Q:** How much can be deducted for a preventive health check-up?

**Reference:** Up to Rs. 5,000 in aggregate, within the health insurance limits; it may be paid in cash (Section 126(3), (9)).

**Answer:**

For a preventive health check-up, an individual assessee can claim a deduction up to Rs. 5000 (five thousand) in aggregate [Section 126].

**Key conditions:**
* The check-up can be for the assessee, the assessee's family (spouse and dependant children), or the assessee's parent or parents [Section 126].
* This amount is part of, and counts towards, the overall limit of Rs. 25000 (25 thousand) allowed for health insurance and preventive check-ups for the assessee/family, or for the parents [Section 126].
* Payment for the preventive health check-up can be made by any mode, including cash [Section 126].

**Retrieved sections:** 125,126; 126; 126; 126; 126; 126,127; 127

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q17 (numeric): UNJUDGED, faithful=None, refused=None
**Q:** What standard deduction is allowed from rental income from a house property?

**Reference:** 30% of the annual value (Section 22(1)(a)). Interest on borrowed capital is also deductible (22(1)(b)).

**Answer:**

I could not find this in the Act.

**Retrieved sections:** 141,142; 142; 142,143; 133,134; 134; 134,135; 21,22; 22; 22; 140,141; 26; 26,27,28; 28,29

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q18 (numeric): UNJUDGED, faithful=None, refused=None
**Q:** What is the maximum rebate a resident individual can get under the new tax regime?

**Reference:** 100% of the tax payable or Rs. 60,000, whichever is less, if income does not exceed twelve lakh rupees; just above that, marginal relief applies (Section 156(2)).

**Answer:**

Under the new tax regime, a resident individual can get a maximum rebate of 100% of the income-tax payable or Rs. 60000, whichever is less [Section 156(1), (2)]. 

**Key conditions:**
* The total income of the resident individual must be chargeable to tax under section 202(1) [Section 156(2)].
* The income must not exceed twelve lakh rupees [Section 156(2)(a)].

**Retrieved sections:** 154,155,156; 155,156; 156,157; 154; 157,158; 2; 2; 2; 202; 202; 202,203

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q19 (lakh): UNJUDGED, faithful=None, refused=None
**Q:** What is the tax rate on income between 8 and 12 lakh under the new regime?

**Reference:** 10% (Section 202(1) Table, Sl. No. 3).

**Answer:**

Under the new tax regime, the tax rates on total income between Rs. 800001 (8 lakh) and Rs. 1200000 (12 lakh) for individuals, Hindu undivided families, and other specified persons are:

* **From Rs. 800001 to Rs. 1200000:** 10% [Section 202(1)]

**Key conditions:**
* This applies unless the person opts out in the manner provided under section 202(4) [Section 202(1)].
* The total income must be computed without certain exemptions, deductions, and set-offs specified under section 202(2).

**Retrieved sections:** 201,202; 202; 202; 201,202; 202; 202,203; 155,156; 156,157; 157,158

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q20 (lakh): UNJUDGED, faithful=None, refused=None
**Q:** Is there a tax rebate if my total income is up to 5 lakh?

**Reference:** Yes. A resident individual gets 100% of the tax or Rs. 12,500, whichever is less, if total income does not exceed Rs. 5,00,000 (Section 156(1)). Under the new regime the limit is twelve lakh rupees with up to Rs. 60,000 (156(2)).

**Answer:**

Yes, an assessee who is an individual resident in India is entitled to a tax rebate [Section 156(1)]. 

**Key conditions:**
* The assessee must be an individual resident in India [Section 156(1)].
* The total income must not exceed Rs. 500000 (5 lakh) [Section 156(1)].
* The deduction is 100% of the income-tax payable or Rs. 12500, whichever is less [Section 156(1)].

**Retrieved sections:** 155,156; 156,157; 157,158; 154,155,156; 393; 393; 393; 3,4,5; 4,5; 5,6; 5,6

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q21 (lakh): UNJUDGED, faithful=None, refused=None
**Q:** At what rate are long-term capital gains on listed shares above 1.25 lakh taxed?

**Reference:** 12.5% on the gains above Rs. 1,25,000, where securities transaction tax was paid (Section 198(2)(a)).

**Answer:**

Long-term capital gains on certain long-term capital assets (such as equity shares in a company where securities transaction tax has been paid on acquisition and transfer) that exceed Rs. 125000 (1.25 lakh) are taxed at the rate of 12.5% [Section 198(1), Section 198(2)]. 

**Key Conditions:**
* The total income must include income chargeable under the head "Capital gains" [Section 198(1)].
* The capital gains must arise from the transfer of a long-term capital asset being an equity share in a company, a unit of an equity-oriented fund, or a unit of a business trust [Section 198(1)].
* Securities transaction tax must have been paid on the acquisition and transfer of the equity share (or on the transfer in the case of a unit of an equity-oriented fund or business trust), unless the transfer is undertaken on a recognised stock exchange located in an International Financial Services Centre with consideration received or receivable in foreign currency, or if the acquisition nature is otherwise specified by the Central Government by notification [Section 198(1), Section 198(4), Section 198(5)].

**Retrieved sections:** 197; 197; 197; 213,214; 214,215; 215; 198; 198; 198; 197,198; 196,197

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q22 (lakh): UNJUDGED, faithful=None, refused=None
**Q:** Is the total deduction for life insurance premium and provident fund contributions capped at 1.5 lakh?

**Reference:** Yes. The sums listed in Schedule XV are deductible up to Rs. 1,50,000 in aggregate (Section 123).

**Answer:**

Yes, the total deduction is capped at Rs. 150000 (1.5 lakh) [Section 123].

**Key Conditions:**
* **Who it applies to:** An individual or a Hindu undivided family [Section 123].
* **Qualifying amounts:** It applies to the aggregate of the sums enumerated in Schedule XV paid or deposited in the tax year [Section 123, Schedule XV].
* **Limit:** The deduction is limited to the whole of the amount paid or restricted to Rs. 150000 (1.5 lakh) if it exceeds that amount, subject to the conditions specified in Schedule XV [Section 123].

**Retrieved sections:** Schedule XV; Schedule XV; Schedule XV; Schedule XV; Schedule XV; Schedule XV; 122,123; 122,123,124; 124; Schedule XV; Schedule XIV,Schedule XV; Schedule XV; Schedule XV

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q23 (out_of_scope): UNJUDGED, faithful=None, refused=None
**Q:** What is the GST rate on restaurant food?

**Reference:** Not covered: GST is a separate law. The app should say it could not find this in the Act.

**Answer:**

I could not find this in the Act.

**Retrieved sections:** 393; 393; 393; 393; 393; 393; 191,192,193; 193; 193; 397; 397; 397; 393; 393; 393

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q24 (out_of_scope): UNJUDGED, faithful=None, refused=None
**Q:** How do I apply for a passport?

**Reference:** Not covered by the Income-tax Act. The app should say it could not find this in the Act.

**Answer:**

I could not find this in the Act.

**Retrieved sections:** 332; 332; 332; 332; 332; 332,333; 332; 332; 524; 524,525; 525,526,527

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q25 (out_of_scope): UNJUDGED, faithful=None, refused=None
**Q:** How is dividend distribution tax under section 115-O calculated?

**Reference:** Not covered: this was a rule of the 1961 Act (abolished in 2020) and is not in the 2025 Act. The app should say it could not find this in the Act.

**Answer:**

I could not find this in the Act.

**Retrieved sections:** 393; 393; 393; 147,148; 148,149; 148,149; 2; 2; 2; 393; 393; 393; 6,7; 7,8; 7,8

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q26 (out_of_scope): UNJUDGED, faithful=None, refused=None
**Q:** What is the wealth tax rate on net wealth above 30 lakh?

**Reference:** Not covered: wealth tax was a separate law, abolished from 2015. The app should say it could not find this in the Act.

**Answer:**

I could not find this in the Act.

**Retrieved sections:** 393; 393; 393; 393; 393; 393; 393; 393; 393; 393; 393; 393; 393; 393

**Judge:** gemini-3.8-flash: daily free-tier quota used up

