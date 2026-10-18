"""Cleaning tests. Snippets are copied from the real PDF (pages 11, 244-245, 469-470, 533)."""

from helpers import make_page

from income_tax_agent.ingest.clean import clean_pages, remove_markers, strip_boilerplate

# Section 202 (p.244) with an omitted item, and its footnote alone on the next page (p.245).
S202_P244 = """    New tax regime for individuals, Hindu undivided family and others.
    202. (1) Irrespective of anything contained in this Act other than Chapter XVII-B
                                       TABLE
       Sl. No.                     Total income                    Rate of tax
        3.     From Rs. 800001 to Rs. 1200000                        10%
          (i) Schedule III (Table: Sl. No. 5 or 6 or 7 or 8 or 11 or 17);
         (iii) 25[***]
         (iv) section 19(1) (Table: Sl. No. 1);"""
S202_P245 = """    25. Omtt. by Act No. 4 of 2026, w.e.f. 1-4-2026. Prior to its omission, sub-clause (iii) read as under :
     "(iii) section 144;\""""


def clean_texts(pages, **kwargs):
    result = clean_pages(pages, **kwargs)
    return [p["text"] for p in result.pages], result.footnotes


def test_strips_header_footer_and_page_counter():
    lines = strip_boilerplate(make_page(12, "    3. (1) For the purposes of this Act")["text"])
    assert lines == ["    3. (1) For the purposes of this Act"]


def test_removes_footnote_with_old_text_and_its_omitted_marker():
    pages = [make_page(244, S202_P244, 1, 2), make_page(245, S202_P245, 2, 2)]
    (p244, p245), footnotes = clean_texts(pages)

    assert "25[" not in p244 and "***" not in p244
    assert "(iii) [omitted]\n" in p244  # The item stays, marked as omitted.
    assert "section 144" not in p244 + p245  # The old, repealed wording is gone.
    assert p245 == ""  # The page held only the footnote.

    assert len(footnotes) == 1
    fn = footnotes[0]
    assert (fn.number, fn.page, fn.quotes_old_text) == ("25", 245, True)
    assert '"(iii) section 144;"' in fn.text


def test_ablation_flag_keeps_footnotes():
    pages = [make_page(244, S202_P244, 1, 2), make_page(245, S202_P245, 2, 2)]
    (p244, p245), footnotes = clean_texts(pages, strip_footnotes=False)
    assert footnotes == []
    assert "25[***]" in p244
    assert "section 144" in p245


def test_inserted_text_keeps_words_but_loses_marker():
    # p.469-470: sub-section (7) was substituted; footnote 85 quotes the old version.
    body = """    84[(a)] The deduction of tax shall not be made under provisions referred to in column C
    85[(7) The person responsible for paying any income shall deliver such declaration
    on or before the seventh day [Table: Sl. No. 1(i)] of the month.]
    (8) Irrespective of anything contained in sub-section (6), the deduction of tax shall not be made
    84. Shall be renumbered as sub-section (6)(a) thereof by Act No. 4 of 2026, w.e.f. 1-4-2027.
    85. Sub. by Act No. 4 of 2026, w.e.f. 1-4-2026. Prior to its substitution, sub-section (7) read as under :
      "(7) The person responsible for paying any income or sum of the nature referred in sub-section (6)\""""
    (text,), footnotes = clean_texts([make_page(469, body)])
    assert text.splitlines() == [
        "(a) The deduction of tax shall not be made under provisions referred to in column C",
        "(7) The person responsible for paying any income shall deliver such declaration",
        "on or before the seventh day [Table: Sl. No. 1(i)] of the month.",
        "(8) Irrespective of anything contained in sub-section (6), the deduction of tax shall not be made",
    ]
    assert [f.number for f in footnotes] == ["84", "85"]
    assert [f.quotes_old_text for f in footnotes] == [False, True]


def test_marker_matching_handles_nested_brackets_and_page_breaks():
    # p.627: "69a[SCHEDULE I ... [See section 9(12)] ... ]" spans pages.
    text = "69a[SCHEDULE I\n[See section 9(12)]\nCONDITIONS\f1. (1) The fund.]\nSCHEDULE II"
    assert remove_markers(text, {"69a"}) == "SCHEDULE I\n[See section 9(12)]\nCONDITIONS\f1. (1) The fund.\nSCHEDULE II"


def test_one_footnote_can_have_several_markers():
    # p.187: footnote 15 covers the same insertion made in three places.
    body = """    Title.
    (b) supplying milk, oilseeds, 15[cotton seed, cattle feed,] fruits; or
    (i) supplying milk, oilseeds, 15[cotton seed, cattle feed,] fruits; or
    15. Ins. by Act No. 4 of 2026, w.e.f. 1-4-2026."""
    (text,), footnotes = clean_texts([make_page(187, body)])
    assert text.count("oilseeds, cotton seed, cattle feed, fruits") == 2
    assert [f.number for f in footnotes] == ["15"]


def test_unknown_marker_numbers_are_left_alone():
    # "2(77)[" and markers without a matching footnote must not be touched.
    assert remove_markers("section 2(77)[a] and 7[x]", {"25"}) == "section 2(77)[a] and 7[x]"


def test_omitted_section_line_is_not_mistaken_for_a_footnote():
    # p.533: the whole of section 447 was omitted. "447." is followed by a footnote line,
    # but "447. 11[***]" itself names no amending Act, so it is body text.
    body = """    Penalty for failure to furnish report under section 172.
    447. 11[***]
    11. Omtt. by Act No. 4 of 2026, w.e.f. 1-4-2026. Prior to its omission, section 447 read as under :
      "447. Penalty for failure to furnish report under section 172.—If any person fails to furnish\""""
    (text,), footnotes = clean_texts([make_page(533, body)])
    assert text == "Penalty for failure to furnish report under section 172.\n447. [omitted]"
    assert [f.number for f in footnotes] == ["11"]


def test_table_columns_are_kept_but_padding_is_shrunk():
    body = """    TABLE
       Sl. No.                     Total income                    Rate of tax
        1.     Upto Rs. 400000                                       Nil"""
    (text,), _ = clean_texts([make_page(244, body)])
    assert text.splitlines() == [
        "TABLE",
        "   Sl. No.  Total income  Rate of tax",
        "    1.  Upto Rs. 400000  Nil",
    ]
