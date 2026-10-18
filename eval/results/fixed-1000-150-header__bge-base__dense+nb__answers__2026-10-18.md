# Answer eval: fixed-1000-150-header__bge-base__dense+nb__answers__2026-10-18

```json
{
  "index": "fixed-1000-150-header__bge-base",
  "mode": "dense",
  "neighbours": true,
  "k": 5,
  "answer_model": "gemini-3.5-flash-lite",
  "judge_model": "gemini-3.8-flash",
  "prompts_sha256": "a8348a7d9097",
  "questions_file": "questions.jsonl",
  "n_questions": 26,
  "n_answered": 26,
  "git_commit": "6e2b6d0",
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
| correct (in scope) | 0.50 (9/18) |
| correct or partial (in scope) | 0.83 (15/18) |
| faithful (all) | 0.94 (17/18) |
| refused, out of scope | 0.00 (0/0) |
| refused, in scope (false refusals) | 0.17 (3/18) |
| unjudged | 8 |

| type | correct | partial | incorrect |
|---|---|---|---|
| table | 0.67 (4/6) | 0.00 (0/6) | 0.33 (2/6) |
| definition | 0.50 (2/4) | 0.25 (1/4) | 0.25 (1/4) |
| prose | 0.25 (1/4) | 0.75 (3/4) | 0.00 (0/4) |
| numeric | 0.50 (2/4) | 0.50 (2/4) | 0.00 (0/4) |

## Every answer

### q01 (table): correct, faithful=True, refused=False
**Q:** What are the income tax rates under the new regime?

**Reference:** Nil up to Rs. 4,00,000; 5% from Rs. 4,00,001 to 8,00,000; 10% to 12,00,000; 15% to 16,00,000; 20% to 20,00,000; 25% to 24,00,000; 30% above Rs. 24,00,000 (Section 202(1) Table).

**Answer:**

Under the new tax regime for individuals, Hindu undivided family, and others, the income tax rates on total income are:

* **Upto Rs. 400000:** Nil [Section 202]
* **From Rs. 400001 to Rs. 800000:** 5% [Section 202]
* **From Rs. 800001 to Rs. 1200000:** 10% [Section 202]
* **From Rs. 1200001 to Rs. 1600000:** 15% [Section 202]
* **From Rs. 1600001 to Rs. 2000000:** 20% [Section 202]
* **From Rs. 2000001 to Rs. 2400000:** 25% [Section 202]
* **Above Rs. 2400000:** 30% [Section 202]

**Retrieved sections:** 201,202; 202; 202; 201,202; 332,333; 333,334; 334,335; 201; 202; 202,203

**Judge:** The app correctly and faithfully sets out all the income tax slabs and corresponding rates under the new tax regime as provided in Section 202.

### q02 (table): correct, faithful=True, refused=False
**Q:** What is the TDS rate when a specified person pays rent for land or a building?

**Reference:** 10% for land, building, furniture or fittings (2% for machinery, plant or equipment). Threshold: Rs. 50,000 for a month or part of a month (Section 393(1) Table, Sl. No. 2(ii)).

**Answer:**

The TDS rate is 10% for the use of any land or building (including factory building), or land appurtenant to a building (including factory building), or furniture, or fittings [Section 393]. 

**Key conditions:**
* The payer must be a specified person paying rent [Section 393].
* The threshold limit is Rs. 50,000 for a month or part of a month [Section 393].

**Retrieved sections:** 393; 393; 393; 2; 2; 2; 397; 397; 397; 393; 19; 19,20; 20,21

**Judge:** The app correctly identifies the 10% TDS rate for land or building rent paid by a specified person, along with the Rs. 50,000 monthly threshold, and all information is fully supported by the excerpts.

### q03 (table): correct, faithful=True, refused=False
**Q:** At what rate is tax collected at source on the sale of scrap?

**Reference:** 2%, collected by the seller (Section 394(1) Table, Sl. No. 4).

**Answer:**

Tax is collected at source on the sale of scrap at the rate of 2% [Section 394].

**Retrieved sections:** 393,394; 394; 394; 394; 394; 394,395; 33; 33; 33; 33

**Judge:** The app accurately answered that tax is collected at source at the rate of 2% on the sale of scrap under Section 394, which is directly supported by the provided excerpts.

### q04 (table): correct, faithful=True, refused=False
**Q:** What is the due date for filing the income tax return of a salaried person with no business income?

**Reference:** 31st July of the financial year after the tax year ("Any other assessee", Section 263(1)(c) Table, Sl. No. 4).

**Answer:**

31st July [Section 263, Excerpt 5 & Excerpt 6].

**Retrieved sections:** 263; 263; 263; 263; 263; 263; 352; 352; 352; 423; 423; 423; 295; 295; 295

**Judge:** The app correctly identifies 31st July as the due date under Section 263, which is fully supported by the provided excerpts.

### q05 (table): incorrect, faithful=True, refused=True
**Q:** How much standard deduction can a salaried employee claim under the new tax regime?

**Reference:** Rs. 75,000 or the salary, whichever is less, when tax is computed under the new regime (section 202(1)); Rs. 50,000 or the salary in any other case (Section 19(1) Table, Sl. No. 2).

**Answer:**

I could not find this in the Act.

**Retrieved sections:** 28,29; 28,29; 29; 146; 146; 146; 144,145,146; 146; 19; 19; 19; 392; 392; 392

**Judge:** The app declined to answer an in-scope question that is addressed by the Act, though the provided excerpts lacked the relevant provisions.

### q06 (table): incorrect, faithful=True, refused=True
**Q:** What is the TCS rate on money sent abroad under the Liberalised Remittance Scheme for education?

**Reference:** 2% for education or medical treatment, and 20% for other purposes, on amounts above ten lakh rupees, collected by the authorised dealer (Section 394(1) Table, Sl. No. 7).

**Answer:**

I could not find this in the Act.

**Retrieved sections:** 191,192,193; 193; 193; 207,208; 207,208; 208; 208,209; 208,209; 209; 209; 209,210; 210; 209

**Judge:** The app declined to answer, but the question is in scope and answered by the Act.

### q07 (definition): correct, faithful=True, refused=False
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
* Every artificial juridical person, not falling within any of the preceding sub-clauses [Section 2]

**Retrieved sections:** 2; 2; 2; 355; 355; 355,356; 127; 127; 127,128; 317,318; 318,319; 318,319; 2

**Judge:** The app's answer accurately lists all the entities included under the definition of 'person' in Section 2(77) of the Act and is fully supported by the excerpts.

### q08 (definition): incorrect, faithful=True, refused=True
**Q:** Who counts as a senior citizen for income tax?

**Reference:** An individual resident in India who is 60 years or older at any time during the tax year (Section 2(100)).

**Answer:**

I could not find this in the Act.

**Retrieved sections:** 402; 402; 402; 393; 393; 393; 393; 393; 393; 393; 3,4,5; 4,5; 5,6

**Judge:** The app incorrectly declined to answer even though the question is within the scope of the Act, but its refusal is faithful to the provided excerpts which do not contain Section 2(100).

### q09 (definition): correct, faithful=True, refused=False
**Q:** What does 'tax year' mean?

**Reference:** The 12-month financial year starting on 1st April. For a new business or new source of income, it runs from the start date to the end of that financial year (Section 3).

**Answer:**

"Tax year" means the twelve months period of the financial year commencing on the 1st April [Section 3].

For a business or profession newly set up, or a source of income newly coming into existence in any financial year, the tax year means the period beginning with the date of setting up of such business or profession, or the date on which such source of income newly comes into existence, and ending with the said financial year [Section 3].

**Retrieved sections:** 2; 2,3,4; 3,4,5; 4,5; 2; 2; 2; 143; 143,144; 144; 332; 332; 332

**Judge:** The answer accurately and faithfully reflects the definition of 'tax year' provided in Section 3 from the excerpts.

### q10 (definition): partial, faithful=True, refused=False
**Q:** Who is a 'relative' of an individual under the Act?

**Reference:** Generally: the husband, wife, brother, sister, or any lineal ascendant or descendant (maternal and paternal) of the individual (Section 2(94)). For gifts, Section 92(5)(g) gives a wider list.

**Answer:**

The term "relative" has different meanings depending on the section of the Act. 

* **For the purposes of Section 355**, "relative" in relation to an individual means [Excerpt 1, Excerpt 2]:
  1. Spouse of the individual [Excerpt 2];
  2. Brother or sister of the individual [Excerpt 2];
  3. Brother or sister of the spouse of the individual [Excerpt 2];
  4. Any lineal ascendant (maternal or paternal) or descendant of the individual [Excerpt 2];
  5. Any lineal ascendant (maternal or paternal) or descendant of the spouse of the individual [Excerpt 2];
  6. Spouse of a person referred to in items 2, 3, 4, or 5 above [Excerpt 2]; and
  7. Any lineal descendant of a brother or sister of either the individual or of the spouse of the individual [Excerpt 2].

* **For the purposes of Section 515**, "relative" in relation to an individual means [Excerpt 6]:
  1. Spouse of the individual [Excerpt 6];
  2. Brother or sister of the individual [Excerpt 6];
  3. Brother or sister of the spouse of the individual [Excerpt 6];
  4. Any lineal ascendant (maternal or paternal) or descendant of the individual [Excerpt 6];
  5. Any lineal ascendant (maternal or paternal) or descendant of the spouse of the individual [Excerpt 6];
  6. Spouse of a person referred to in items 2, 3, 4, or 5 above [Excerpt 6]; and
  7. Any lineal descendant of a brother or sister of either the individual or the spouse of the individual [Excerpt 6].

* **For the purposes of Section 92**, a "relative" in the case of an individual means [Excerpt 8, Excerpt 9]:
  1. Spouse [Excerpt 9];
  2. Brother or sister [Excerpt 9];
  3. Brother or sister of the spouse [Excerpt 9];
  4. Brother or sister of either of the parents [Excerpt 9];
  5. Any lineal ascendant (maternal as well as paternal) or descendant [Excerpt 9];
  6. Any lineal ascendant (maternal as well as paternal) or descendant of the spouse [Excerpt 9]; and
  7. Spouse of the person referred to in items 2 to 6 above [Excerpt 9].

*(Note: These definitions apply only within their respective sections and are not the general meaning for the entire Act.)*

**Retrieved sections:** 355; 355; 355; 355; 515; 515,516; 516,517,518,519; 92; 92,93; 93; 99; 99; 99,100

**Judge:** The app correctly detailed the definition under Section 92 (and other specific sections), but missed the general definition under Section 2(94) mentioned in the reference answer.

### q11 (prose): partial, faithful=True, refused=False
**Q:** How many days must an individual stay in India to be treated as a resident?

**Reference:** 182 days or more in the tax year, or 60 days in the year plus 365 days in total over the previous four years (Section 6(2)), with exceptions in 6(3) to 6(5).

**Answer:**

An individual is treated as a resident in India in a tax year if they meet either of the following conditions:

* They are in India for a total period of **182 days or more** in that tax year [Section 6].
* They are in India cumulatively for **60 days or more** during that tax year **and** cumulatively for **365 days or more** in the four years preceding that tax year [Section 6].

**Retrieved sections:** 6; 6; 6,7; 6; 6; 5,6; 5,6; 7,8

**Judge:** The app correctly provides the two primary day-count tests under Section 6(2), but it omits the exceptions and modifications under subsections (3) to (5) that change the applicable day requirements.

### q12 (prose): partial, faithful=True, refused=False
**Q:** When does the Income-tax Act, 2025 come into force?

**Reference:** On 1st April, 2026, unless the Act says otherwise for a provision (Section 1(3)).

**Answer:**

The Income-tax Act, 2025 comes into force on the 1st April, 2026 [Section 1(3)].

**Retrieved sections:** 1,2; 2; 536; 536; 536; 200,201; 201; 201; 536; 536; 536; 536

**Judge:** The app correctly identifies the commencement date of 1st April, 2026 under Section 1(3), but omits the statutory qualification that this applies save as otherwise provided in the Act.

### q13 (prose): partial, faithful=False, refused=False
**Q:** Can someone with business income opt out of the new tax regime and later switch back?

**Reference:** Yes, once. They opt out by the return due date; the choice then applies to later years; it can be withdrawn only once; after that they can never opt out again, unless they stop having business income (Section 202(4)(a)).

**Answer:**

Yes, a person with income from business or profession may withdraw the option once, but after such withdrawal, they shall never be eligible to exercise the option again under that sub-section [Section 202(4)(a)(iii), (iv)]. 

**Key conditions:**
* The withdrawal can be made for a tax year other than the tax year for which the option was exercised [Section 202(4)(a)(iii)].
* The restriction against switching back does not apply if the person permanently ceases to have any income from business or profession, in which case a different option becomes available [Section 202(4)(a)(iv)].

**Retrieved sections:** 318,319; 319,320; 320; 202; 202; 202,203; 332,333; 333,334; 334,335; 352; 352; 352; 203

**Judge:** The app incorrectly refers to the post-withdrawal restriction as a 'restriction against switching back' (the restriction actually prevents opting out again after switching back), adds the unsupported word 'permanently', and misses the return due date timing requirement for the initial opt-out.
**Unsupported claims:** ['The restriction against switching back does not apply if the person permanently ceases to have any income from business or profession']

### q14 (prose): correct, faithful=True, refused=False
**Q:** What happens to the old Income-tax Act, 1961?

**Reference:** It is repealed, but past actions, rights and liabilities, and pending proceedings under it are saved (Section 536).

**Answer:**

The Income-tax Act, 1961 is repealed [Section 536]. 

**Key Conditions:**
* Previous operations, rights, privileges, obligations, and liabilities under the repealed Act remain unaffected [Section 536].
* Pending and new proceedings (such as assessments, appeals, and penalties) for tax years beginning before April 1, 2026, continue to be governed and carried out under the procedure of the repealed Act [Section 536].

**Retrieved sections:** 534,535; 535,536; 536; 536; 536; 536; 536; 536; 536; 536; 536

**Judge:** The app correctly and faithfully states that the Income-tax Act, 1961 is repealed under Section 536, while past operations, rights, liabilities, and pending proceedings are saved.

### q15 (numeric): partial, faithful=True, refused=False
**Q:** What is the maximum deduction for health insurance premium paid for parents?

**Reference:** Rs. 25,000, or Rs. 50,000 if the parent is a senior citizen. Together with medical expenditure for parents, the total is capped at Rs. 50,000 (Section 126(2)(b), (4), (8)).

**Answer:**

The maximum deduction for health insurance premium and preventive health check-up paid for parent or parents is Rs. 25000 in aggregate [Section 126, Excerpt 4].

Key conditions:
* If the parent is a senior citizen, the limit of Rs. 25000 is substituted with Rs. 50000 [Section 126].
* Payment must be made by a mode other than cash (except for preventive health check-up, which can be paid in cash) [Section 126].

**Retrieved sections:** 126; 126; 126; 126; 125,126; 125; 126,127

**Judge:** The app correctly identifies the limits of Rs. 25,000 and Rs. 50,000 for senior citizens, but omits the overall aggregate cap of Rs. 50,000 combined with medical expenditure under Section 126(4).

### q16 (numeric): correct, faithful=True, refused=False
**Q:** How much can be deducted for a preventive health check-up?

**Reference:** Up to Rs. 5,000 in aggregate, within the health insurance limits; it may be paid in cash (Section 126(3), (9)).

**Answer:**

Yes, a deduction for a preventive health check-up is allowed up to Rs. 5000 in aggregate [Section 126].

**Key Conditions:**
* It applies to amounts paid for preventive health check-ups for the assessee, their family, or their parent or parents [Section 126].
* The payment can be made by any mode, including cash [Section 126].
* This amount is part of, and counts towards, the overall limits specified for health insurance and check-ups for the assessee/family (up to Rs. 25000) or parents (up to Rs. 25000) [Section 126].

**Retrieved sections:** 125,126; 126; 126; 126; 126; 126,127; 127

**Judge:** The app's answer accurately captures all the key facts from the reference answer and excerpts, including the Rs. 5,000 aggregate limit, the inclusion of cash payments, and the interaction with overall limits under Section 126.

### q17 (numeric): correct, faithful=True, refused=False
**Q:** What standard deduction is allowed from rental income from a house property?

**Reference:** 30% of the annual value (Section 22(1)(a)). Interest on borrowed capital is also deductible (22(1)(b)).

**Answer:**

A standard deduction of 30% of the annual value is allowed from income under the head "Income from house property" [Section 22].

**Retrieved sections:** 141,142; 142; 142,143; 133,134; 134; 134,135; 21,22; 22; 22; 140,141; 26; 26,27,28; 28,29

**Judge:** The app correctly identifies the standard deduction of 30% of the annual value under Section 22, fully supported by the excerpts.

### q18 (numeric): partial, faithful=True, refused=False
**Q:** What is the maximum rebate a resident individual can get under the new tax regime?

**Reference:** 100% of the tax payable or Rs. 60,000, whichever is less, if income does not exceed twelve lakh rupees; just above that, marginal relief applies (Section 156(2)).

**Answer:**

A resident individual can get a maximum rebate of Rs. 60000 under the new tax regime [Section 156(2)].

**Key Conditions:**
* The total income of the resident individual assessee must be chargeable to tax under section 202(1) [Section 156(2)].
* The rebate is 100% of the income-tax payable or Rs. 60000, whichever is less [Section 156(2)(a)].

**Retrieved sections:** 154,155,156; 155,156; 156,157; 154; 157,158; 2; 2; 2; 202; 202; 202,203

**Judge:** The app correctly identifies the maximum rebate cap of Rs. 60,000 or 100% of tax payable, but it misses the key condition that total income must not exceed twelve lakh rupees and omits marginal relief.

### q19 (lakh): UNJUDGED, faithful=None, refused=None
**Q:** What is the tax rate on income between 8 and 12 lakh under the new regime?

**Reference:** 10% (Section 202(1) Table, Sl. No. 3).

**Answer:**

This may be incomplete: the excerpts show only part of the table.

The tax rate on total income between Rs. 800001 (8 lakh) and Rs. 1200000 (12 lakh) under the new tax regime for individuals, Hindu undivided families, and others is 10% [Section 202(1)].

**Key Conditions:**
* The total income is computed without specified exemptions, deductions, and set-offs of certain carried forward losses, depreciation, or house property losses [Section 202(2)].
* The person must not opt out of the regime according to the prescribed rules [Section 202(1), (4)].

**Retrieved sections:** 201,202; 202; 202; 201,202; 202; 202,203; 155,156; 156,157; 157,158

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q20 (lakh): UNJUDGED, faithful=None, refused=None
**Q:** Is there a tax rebate if my total income is up to 5 lakh?

**Reference:** Yes. A resident individual gets 100% of the tax or Rs. 12,500, whichever is less, if total income does not exceed Rs. 5,00,000 (Section 156(1)). Under the new regime the limit is twelve lakh rupees with up to Rs. 60,000 (156(2)).

**Answer:**

Yes, a tax rebate is available if your total income does not exceed Rs. 500000 (5 lakh) [Section 156(1)].

**Key conditions:**
* You must be an individual resident in India [Section 156(1)].
* Your total income must not exceed Rs. 500000 (5 lakh) [Section 156(1)].
* The rebate is 100% of the income-tax payable or Rs. 12500, whichever is less [Section 156(1)].

**Retrieved sections:** 155,156; 156,157; 157,158; 154,155,156; 393; 393; 393; 3,4,5; 4,5; 5,6; 5,6

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q21 (lakh): UNJUDGED, faithful=None, refused=None
**Q:** At what rate are long-term capital gains on listed shares above 1.25 lakh taxed?

**Reference:** 12.5% on the gains above Rs. 1,25,000, where securities transaction tax was paid (Section 198(2)(a)).

**Answer:**

Long-term capital gains on listed shares exceeding Rs. 125000 (1.25 lakh) are taxed at the rate of 12.5% [Section 198].

**Key Conditions:**
* The total income must include income chargeable under the head "Capital gains" arising from the transfer of a long-term capital asset, being an equity share in a company, a unit of an equity-oriented fund, or a unit of a business trust [Section 198(1)].
* Securities transaction tax under Chapter VII of the Finance (No. 2) Act, 2004 must have been paid (in the case of equity shares, paid on both acquisition and transfer, except where specific exemptions apply such as certain transfers on a recognised stock exchange in an International Financial Services Centre with consideration in foreign currency or specified by the Central Government) [Section 198(1), (4), (5)].

**Retrieved sections:** 197; 197; 197; 213,214; 214,215; 215; 198; 198; 198; 197,198; 196,197

**Judge:** gemini-3.8-flash: daily free-tier quota used up

### q22 (lakh): UNJUDGED, faithful=None, refused=None
**Q:** Is the total deduction for life insurance premium and provident fund contributions capped at 1.5 lakh?

**Reference:** Yes. The sums listed in Schedule XV are deductible up to Rs. 1,50,000 in aggregate (Section 123).

**Answer:**

Yes, the deduction for the aggregate of the sums enumerated in Schedule XV (which includes life insurance premia and provident fund contributions) is capped at Rs. 150000 (1.5 lakh) [Section 123, Schedule XV]. 

**Key conditions:**
* It applies to individuals and Hindu undivided families [Section 123].
* It is allowed while computing the total income for the tax year for the whole of the amount paid or deposited, up to the specified limit [Section 123].
* Life insurance policies are subject to specific limits on the capital sum assured (such as up to 20% for policies issued on or before March 31, 2012, up to 10% for policies issued on or after April 1, 2012, or up to 15% for policies covering persons with disability, severe disability, or specified diseases/ailments) [Schedule XV, Paragraph 2].

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

