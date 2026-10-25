"""Find where each section starts, so any text position maps to a section and a page.

A section in the PDF looks like this:

    New tax regime for individuals, Hindu undivided family and others.    <- title line
    202. (1) Irrespective of anything contained in this Act...             <- number line

Spacing varies ("94 . The ...", "427.(1) Without ..."), and an omitted section can be
just "447." after cleaning. Tables also have numbered rows ("1. Sale of scrap."). To tell
them apart we walk the text in order and only accept the *next* expected section number,
right after a title line. The Act has sections 1 to 536 with no gaps.

After the sections come the Schedules. They number their items 1, 2, 3 again, so once the
first "SCHEDULE I" heading appears we stop looking for sections and label text by schedule.

Sections are grouped under headings that sit above a section's title line:

    CHAPTER XIII                                                  <- chapter
    DETERMINATION OF TAX IN SPECIAL CASES                         <- its title
    E.—Special provisions relating to non-residents and foreign companies   <- part (optional)
    1.—Legal representatives                                      <- sub-part (Chapters XVII, XVIII)

Many section titles only make sense under their heading: Section 214 is "Tax on investment
income and long-term capital gains."; only Part E says it is about non-residents. So each
section records its heading path, and the headings belong to the section they introduce
(not to the end of the one before).
"""

import re
from bisect import bisect_right
from dataclasses import dataclass, field
from functools import cached_property

SECTION_RE = re.compile(r"^\s*(\d+)\s*\.(?!\d)")
SCHEDULE_RE = re.compile(r"^\s*SCHEDULE ([IVXL]+)\s*$")
# Lines under a "SCHEDULE XI" heading that are not its title.
NOT_TITLE_RE = re.compile(r"^\s*(\[See section|PART [A-Z]+\s*$)")
CHAPTER_RE = re.compile(r"^\s*CHAPTER ([IVXL]+)\s*$")
# The em dash tells headings from table rows: "E.—Special ...", "B. —Special ...", "1. —Registration".
PART_RE = re.compile(r"^\s*([A-Z])\.\s*—\s*(\S.*?)\s*$")
SUBPART_RE = re.compile(r"^\s*(\d+)\.\s*—\s*(\S.*?)\.?\s*$")


@dataclass
class SectionStart:
    number: str  # "202", or "Schedule II" for schedules
    title: str
    page: int
    offset: int  # character offset in Document.text where the section begins (its headings, else title)
    # Headings above the section, outermost first, e.g. ["Chapter XIII: Determination of tax
    # in special cases", "E. Special provisions relating to non-residents and foreign companies"].
    path: list[str] = field(default_factory=list)


@dataclass
class Document:
    """All cleaned pages joined into one string, with lookups by character offset."""

    text: str
    page_offsets: list[int]  # start offset of each non-empty page
    page_numbers: list[int]  # PDF page number for each entry in page_offsets
    sections: list[SectionStart]

    def page_at(self, offset: int) -> int:
        return self.page_numbers[bisect_right(self.page_offsets, offset) - 1]

    def pages_between(self, start: int, end: int) -> list[int]:
        """PDF pages covered by text[start:end]."""
        first = bisect_right(self.page_offsets, start) - 1
        last = bisect_right(self.page_offsets, max(start, end - 1)) - 1
        return self.page_numbers[first : last + 1]

    @cached_property
    def _section_offsets(self) -> list[int]:
        return [s.offset for s in self.sections]

    def section_at(self, offset: int) -> SectionStart | None:
        """The section that contains this offset, or None for text before section 1."""
        i = bisect_right(self._section_offsets, offset) - 1
        return self.sections[i] if i >= 0 else None

    def sections_between(self, start: int, end: int) -> list[SectionStart]:
        """Sections that overlap text[start:end]. A chunk crossing a boundary gets both."""
        first = max(bisect_right(self._section_offsets, start) - 1, 0)
        last = bisect_right(self._section_offsets, max(start, end - 1)) - 1
        return self.sections[first : last + 1] if last >= 0 else []

    def section_chars_between(self, start: int, end: int) -> dict[str, int]:
        """How many characters of text[start:end] fall in each section.

        Whitespace is not counted, so table padding does not inflate a section's share.
        The title page before section 1 is counted as part of section 1, like
        sections_between does.
        """
        counts: dict[str, int] = {}
        first = max(bisect_right(self._section_offsets, start) - 1, 0)
        for i in range(first, len(self.sections)):
            sec_start = self.sections[i].offset if i > 0 else 0
            if sec_start >= end:
                break
            sec_end = self.sections[i + 1].offset if i + 1 < len(self.sections) else len(self.text)
            span = self.text[max(start, sec_start) : min(end, sec_end)]
            n = sum(not ch.isspace() for ch in span)
            if n:
                counts[self.sections[i].number] = n
        return counts


def _looks_like_title(line: str) -> bool:
    """Section titles are plain sentences, not clauses "(a) ..." or numbered rows "3. ..."."""
    s = line.strip()
    return len(s) > 3 and not s.startswith("(") and not SECTION_RE.match(s)


def _chapter_title(lines: list[str], i: int) -> str:
    """The first non-empty line after "CHAPTER XIII", in sentence case."""
    title = next((l.strip() for l in lines[i + 1 : i + 4] if l.strip()), "")
    return title.capitalize()


def find_section_starts(lines: list[str], line_offsets: list[int], line_pages: list[int]) -> list[SectionStart]:
    starts: list[SectionStart] = []
    expected = 1
    in_schedules = False
    chapter, part, subpart = "", "", ""
    heading_offset: int | None = None  # first heading line since the last section start
    for i, line in enumerate(lines):
        if not in_schedules:
            # Schedules have their own "A.—" parts; those are not the Act's chapters.
            heading = True
            if m := CHAPTER_RE.match(line):
                chapter, part, subpart = f"Chapter {m.group(1)}: {_chapter_title(lines, i)}", "", ""
            elif m := PART_RE.match(line):
                part, subpart = f"{m.group(1)}. {m.group(2)}", ""
            elif m := SUBPART_RE.match(line):
                subpart = f"{m.group(1)}. {m.group(2)}"
            else:
                heading = False
            if heading and heading_offset is None:
                heading_offset = line_offsets[i]

        sched = SCHEDULE_RE.match(line)
        if sched:
            in_schedules = True
            # The title is the first line that is not "[See section ...]" or "PART A".
            # (Schedules XI and XII open with "PART A" before their real title.)
            title = next(
                (l.strip() for l in lines[i + 1 : i + 5] if not NOT_TITLE_RE.match(l)), ""
            )
            starts.append(
                SectionStart(f"Schedule {sched.group(1)}", title, line_pages[i], line_offsets[i])
            )
            continue
        if in_schedules or i == 0:
            continue
        m = SECTION_RE.match(line)
        if m and int(m.group(1)) == expected and _looks_like_title(lines[i - 1]):
            offset = line_offsets[i - 1] if heading_offset is None else min(heading_offset, line_offsets[i - 1])
            path = [p for p in (chapter, part, subpart) if p]
            starts.append(SectionStart(m.group(1), lines[i - 1].strip(), line_pages[i], offset, path))
            expected += 1
            heading_offset = None
    return starts


def build_document(pages: list[dict]) -> Document:
    """Join cleaned pages into a Document and detect section boundaries."""
    parts, page_offsets, page_numbers = [], [], []
    lines, line_offsets, line_pages = [], [], []
    offset = 0
    for page in pages:
        if not page["text"]:
            continue  # Pages that held only footnotes are empty after cleaning.
        page_offsets.append(offset)
        page_numbers.append(page["page"])
        for line in page["text"].split("\n"):
            lines.append(line)
            line_offsets.append(offset)
            line_pages.append(page["page"])
            offset += len(line) + 1  # +1 for the "\n" that joins lines
        parts.append(page["text"])
    text = "\n".join(parts)
    sections = find_section_starts(lines, line_offsets, line_pages)
    return Document(text, page_offsets, page_numbers, sections)
