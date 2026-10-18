"""Section detection tests, using the spacing quirks found in the real PDF."""

from income_tax_agent.ingest.sections import build_document


def doc_from(*pages: tuple[int, str]):
    return build_document([{"page": n, "text": t} for n, t in pages])


SECTIONS_1_TO_3 = """Short title, extent and commencement.
1. (1) This Act may be called the Income-tax Act, 2025.
Definitions.
2.(1) In this Act, unless the context otherwise requires,—
TABLE
 1. Sale of scrap.  Seller.  2%
 3. Sale of timber.  Seller.  2%"""

SECTION_3 = """Definition of "tax year".
3 . (1) For the purposes of this Act, "tax year" means the twelve months period."""


def test_detects_sections_with_odd_spacing_and_skips_table_rows():
    doc = doc_from((1, SECTIONS_1_TO_3), (12, SECTION_3))
    assert [(s.number, s.title, s.page) for s in doc.sections] == [
        ("1", "Short title, extent and commencement.", 1),
        ("2", "Definitions.", 1),
        ("3", 'Definition of "tax year".', 12),  # "3 ." on p.12, not the "3." table row on p.1
    ]


def test_section_without_text_after_number():
    # Omitted sections are just "447." after cleaning. Here: section 1 has no body text.
    doc = doc_from((533, "Penalty for failure to furnish report under section 172.\n1."))
    assert [s.number for s in doc.sections] == ["1"]


def test_schedule_items_are_not_sections():
    text = SECTIONS_1_TO_3 + "\nSCHEDULE I\n[See section 9(12)]\nCONDITIONS FOR CERTAIN ACTIVITIES\nTitle.\n3. (1) An item."
    doc = doc_from((627, text))
    assert [s.number for s in doc.sections] == ["1", "2", "Schedule I"]
    assert doc.sections[-1].title == "CONDITIONS FOR CERTAIN ACTIVITIES"


def test_schedule_title_skips_part_heading():
    doc = doc_from((659, "SCHEDULE XI\n[See section 2(91)]\nPART A\nRECOGNISED PROVIDENT FUNDS\nApplication of Part"))
    assert doc.sections[0].title == "RECOGNISED PROVIDENT FUNDS"


def test_lookup_by_offset_lists_both_sections_at_a_boundary():
    doc = doc_from((1, SECTIONS_1_TO_3), (12, SECTION_3))
    start_2 = doc.text.index("Definitions.")
    assert doc.section_at(0).number == "1"
    assert doc.section_at(start_2).number == "2"
    # A span that crosses from section 2 into section 3 (and page 1 into page 12).
    start = doc.text.index("Sale of scrap")
    end = doc.text.index("For the purposes")
    assert [s.number for s in doc.sections_between(start, end)] == ["2", "3"]
    assert doc.pages_between(start, end) == [1, 12]
    assert doc.pages_between(0, 5) == [1]
