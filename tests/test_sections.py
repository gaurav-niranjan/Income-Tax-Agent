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


# Real headings from p.231 and p.254, and the sub-parts of Chapter XVII (p.366).
CHAPTERS = """Definition of "tax year".
3 . (1) For the purposes of this Act, "tax year" means the twelve months period.
CHAPTER XIII
DETERMINATION OF TAX IN SPECIAL CASES
A.—Determination of tax in certain special cases
Determination of tax where total income includes income on which no tax is payable.
4. (1) In a case where the total income of an assessee includes any income.
Tax on short-term capital gains in certain cases.
5. Where the total income of an assessee includes short-term capital gains.
                    E.—Special provisions relating to non-residents and foreign companies
Tax on dividends, royalty and fees for technical service in case of foreign companies.
6. (1) The income-tax payable on the total income of a non-resident.
CHAPTER XVII
SPECIAL PROVISIONS RELATING TO CERTAIN PERSONS
B. —Special provisions for registered non-profit organisation
1. —Registration
Application for registration.
7. (1) An application for registration."""


def test_sections_record_chapter_part_and_sub_part():
    doc = doc_from((1, SECTIONS_1_TO_3), (231, CHAPTERS))
    paths = {s.number: s.path for s in doc.sections}
    assert paths["3"] == []
    assert paths["4"] == paths["5"] == [
        "Chapter XIII: Determination of tax in special cases",
        "A. Determination of tax in certain special cases",
    ]
    assert paths["6"] == [
        "Chapter XIII: Determination of tax in special cases",
        "E. Special provisions relating to non-residents and foreign companies",
    ]
    # A new chapter clears the part; "B. —" and "1. —" spacing both work.
    assert paths["7"] == [
        "Chapter XVII: Special provisions relating to certain persons",
        "B. Special provisions for registered non-profit organisation",
        "1. Registration",
    ]


def test_headings_belong_to_the_section_they_introduce():
    doc = doc_from((1, SECTIONS_1_TO_3), (231, CHAPTERS))
    # Part E's heading is not the end of section 5 (its text would match "non-residents").
    e_heading = doc.text.index("E.—Special")
    assert doc.section_at(e_heading).number == "6"
    chapter = doc.text.index("CHAPTER XIII")
    assert doc.section_at(chapter).number == "4"
    assert doc.section_at(chapter - 1).number == "3"


def test_schedule_parts_are_not_chapter_parts():
    text = SECTION_3 + "\nSCHEDULE XIV\n[See section 4]\nINSURANCE BUSINESS\nA.—Life insurance business\n1. Profits."
    doc = doc_from((1, SECTIONS_1_TO_3), (640, text))
    assert [(s.number, s.path) for s in doc.sections][-2:] == [("3", []), ("Schedule XIV", [])]


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
