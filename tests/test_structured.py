"""Structured chunker: detection traps found in the real Act, packing, tables, labels."""

import json

from helpers import make_page

from income_tax_agent.config import Settings
from income_tax_agent.embeddings import FakeEmbeddings
from income_tax_agent.index import build_index
from income_tax_agent.ingest.chunkers.structured import StructuredChunker, size, split_items
from income_tax_agent.ingest.sections import build_document

FILLER = " ".join(f"word{i}" for i in range(25))  # ~200 chars

# Sub-section traps from the real text: "(1)(a)" with no space (Section 263), a wrapped
# reference line "(1) was received." (Section 231), and a gap where (4) was omitted.
SUBSECTIONS = f"""Return of income.
1. (1)(a) Every person shall furnish a return {FILLER}.
(2) An order under this section shall be passed within three months from the end of the month in which the application under sub-section
(1) was received.
(3) Every claim for refund {FILLER}.
(5) Save as otherwise provided {FILLER}."""

# Section 2: each definition its own chunk; the opening line joins the first one.
DEFINITIONS = """Definitions.
2. In this Act, unless the context otherwise requires,—
  (1) "accountant" shall have the meaning assigned to it in section 515(3)(b);
  (2) "Additional Commissioner" means a person appointed under section 237(1);
 (10) "senior citizen" means an individual resident in India who is of the age of sixty years or more;"""

# Section 202's slab table: rows "1.", then the next sub-section "(2)" after a row.
SLABS = """New tax regime for individuals.
3. (1) The income-tax payable shall be computed at the rate of tax given in the following Table:—
                                   TABLE
   Sl. No.  Total income  Rate of tax
     A  B  C
    1.  Upto Rs. 400000  Nil
    2.  From Rs. 400001 to Rs. 800000  5%
    3.  From Rs. 800001 to Rs. 1200000  10%
    4.  From Rs. 1200001 to Rs. 1600000  15%
    5.  From Rs. 1600001 to Rs. 2000000  20%
    6.  From Rs. 2000001 to Rs. 2400000  25%
    7.  Above Rs. 2400000  30%
(2) For the purposes of sub-section (1), the total income shall be computed without any exemption."""

# Section 206: a table whose rows are numbered "(1)", "(2)" like sub-sections.
PAREN_TABLE = """Alternate minimum tax.
4. (1) The amounts in column A shall be added and those in column B reduced:
                                   TABLE
            Amounts (to be added)  Amounts (to be reduced)
                  (A)  (B)
(1) Amounts credited to the statement of profit and loss. (1) Amounts debited.
(2) The amounts debited on distribution. (2) The amounts credited on distribution.
(3) One-fifth of the transition amount. (3) One-fifth of the transition amount.
(2) (a) Irrespective of anything contained in this Act, the regular income-tax payable shall be computed."""

SCHEDULE = """SCHEDULE III
[See section 11]
INCOME NOT TO BE INCLUDED IN TOTAL INCOME
                                   TABLE
Sl. No.  Income  Eligible persons  Conditions
 A  B  C  D
1.  Any sum received by a member from Hindu undivided family. An individual. Nil.
2.  Any sum received by a partner. A partner. Nil.
2A. Disability pension received. A member of the armed forces. Nil.
Note 1.—For the purposes of Sl. No. 2A, the expression "disability" has the meaning given."""


def _doc(*parts: str):
    return build_document([{"page": 1, "text": "\n".join(parts)}])


def _refs(doc, number: str) -> list[str]:
    i = [s.number for s in doc.sections].index(number)
    start = doc.sections[i].offset
    end = doc.sections[i + 1].offset if i + 1 < len(doc.sections) else len(doc.text)
    return [it.ref for it in split_items(doc.text[start:end], start, number)]


def test_subsections_skip_wrapped_references_and_allow_gaps():
    doc = _doc(SUBSECTIONS)
    assert _refs(doc, "1") == ["", "(1)", "(2)", "(3)", "(5)"]


def test_table_rows_and_the_subsection_after_them():
    doc = _doc(SUBSECTIONS, DEFINITIONS, SLABS)
    refs = _refs(doc, "3")
    assert refs[:3] == ["", "(1)", "(1) Table"]
    assert refs[3:10] == [f"(1) Table, Sl. No. {n}" for n in range(1, 8)]
    assert refs[10] == "(2)"


def test_paren_numbered_table_rows_are_not_subsections():
    doc = _doc(SUBSECTIONS, DEFINITIONS, SLABS, PAREN_TABLE)
    refs = _refs(doc, "4")
    assert refs[3:6] == ["(1) Table, Sl. No. 1", "(1) Table, Sl. No. 2", "(1) Table, Sl. No. 3"]
    assert refs[-1] == "(2)"  # the real sub-section (2), after the table


def test_schedule_rows_with_letter_suffix_and_notes():
    doc = _doc(SUBSECTIONS, SCHEDULE)
    assert _refs(doc, "Schedule III")[1:] == [
        "Table",
        "Table, Sl. No. 1",
        "Table, Sl. No. 2",
        "Table, Sl. No. 2A",
        "Table, Note",
    ]


def test_definitions_stand_alone_and_opening_text_joins_the_first():
    doc = _doc(SUBSECTIONS, DEFINITIONS)
    chunks = [c for c in StructuredChunker(max_chars=150, min_chars=40).chunk(doc) if c.sections == ["2"]]
    assert [c.extra["label"] for c in chunks] == ["Section 2(1)", "Section 2(2)", "Section 2(10)"]
    assert chunks[0].text.startswith("Definitions.\n2. In this Act")
    assert chunks[2].text.startswith('(10) "senior citizen" means')
    assert chunks[2].search_text.startswith("Section 2(10): Definitions.\n")


def test_small_section_is_one_chunk_and_chunks_never_cross_sections():
    doc = _doc(SUBSECTIONS, DEFINITIONS, SLABS, PAREN_TABLE)
    chunks = StructuredChunker(max_chars=2000, min_chars=40).chunk(doc)
    assert [c.sections for c in chunks] == [["1"], ["2"], ["3"], ["4"]]
    assert all(c.extra["label"] == f"Section {c.sections[0]}" for c in chunks)
    # Every non-space character is in exactly one chunk.
    total = sum(sum(c.extra["section_chars"].values()) for c in chunks)
    assert total == sum(not ch.isspace() for ch in doc.text)


def test_split_table_repeats_its_header():
    doc = _doc(SUBSECTIONS, DEFINITIONS, SLABS)
    chunks = [c for c in StructuredChunker(max_chars=250, min_chars=40).chunk(doc) if c.sections == ["3"]]
    later = [c for c in chunks if c.extra["repeated_header"]]
    assert later, "the slab table should be split, with the header repeated"
    for c in later:
        assert c.text.lstrip().startswith("TABLE\n   Sl. No.  Total income  Rate of tax")
        assert "Table, Sl. No." in c.extra["label"]
    # Every slab row is in some chunk, and no chunk is far over the limit.
    assert all(any(f"{n}.  " in c.text for c in chunks) for n in range(1, 8))
    assert all(size(c.text) <= 250 * 1.25 for c in chunks)


def test_small_tail_merges_into_the_chunk_before():
    doc = _doc(SUBSECTIONS)
    chunks = StructuredChunker(max_chars=450, min_chars=300).chunk(doc)
    assert all(size(c.text) >= 300 for c in chunks)


def test_build_structured_index(tmp_path):
    settings = Settings(index_dir=tmp_path, _env_file=None)
    pages = [make_page(1, "\n".join([SUBSECTIONS, DEFINITIONS, SLABS]))]
    out = build_index(StructuredChunker(300, 60), FakeEmbeddings(), settings, pages=pages)
    assert out.name == "structured-300__fake"
    manifest = json.loads((out / "manifest.json").read_text())
    assert manifest["chunker"]["type"] == "structured"
    assert manifest["stats"]["n_chunks_multi_section"] == 0
