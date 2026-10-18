"""Clean the raw page text.

What gets removed:
1. Page boilerplate: the header, the "Downloaded/Printed on ..." footer and "Page N of N".
2. Amendment footnotes. Many quote the old, repealed wording ("Prior to its substitution,
   clause (32) read as under: ..."). Left in, the app could answer with old law.
3. The in-text markers that point to those footnotes: `25[***]` (text omitted) becomes
   `[omitted]`, and `85[(7) The person ...]` (text inserted or substituted) keeps its words
   but loses `85[` and the matching `]`. One footnote can have several markers when the
   same change was made in several places.

The PDF is 553 per-section printouts stitched together, and every printout puts its
footnotes in one block at its end. So we clean one printout at a time.
"""

import re
from dataclasses import dataclass, field

HEADER_RE = re.compile(r"^\s*(Income Tax Department|Ministry of Finance, Government of India)\s*$")
FOOTER_RE = re.compile(r"^\s*Downloaded/Printed on \d")
PAGE_COUNTER_RE = re.compile(r"Page (\d+) of (\d+)\s*$")

# A footnote starts like "1. Sub. by ...", "10a. Ins. by ...", "51.. Sub. for ..." and names
# the amending law on the same line, e.g. "by Act No. 4 of 2026" or
# "by the Tribunals Reforms Act, 2026".
FOOTNOTE_START_RE = re.compile(r"^\s*(\d+[a-z]?)\.{1,2}\s+\S")
AMENDING_ACT_RE = re.compile(r"\bby (the )?(Act No\.|[A-Z][A-Za-z ]*Act, \d{4})")
# "Prior to its substitution, clause (32) read as under :" -> the footnote quotes old law.
QUOTES_OLD_TEXT_RE = re.compile(r"read as under|Prior to (its|their)", re.I)

# A marker is a footnote number glued to an opening bracket: "25[", "88a[".
# The look-behind stops "2(77)[" or "abc1[" from matching.
MARKER_RE = re.compile(r"(?<![\w(])(\d+[a-z]?)\[")

# Joins the pages of one printout so markers can be matched across page breaks.
PAGE_BREAK = "\f"
# Replaces "25[***]".
OMITTED = "[omitted]"


@dataclass
class Footnote:
    number: str  # "25", "88a"
    page: int  # page where the footnote starts
    text: str  # the full footnote, lines joined with "\n"

    @property
    def quotes_old_text(self) -> bool:
        return bool(QUOTES_OLD_TEXT_RE.search(self.text))


@dataclass
class CleanResult:
    pages: list[dict]  # [{"page": n, "text": cleaned text}], same order as the input
    footnotes: list[Footnote] = field(default_factory=list)  # what was removed


def group_printouts(pages: list[dict]) -> list[list[dict]]:
    """Split pages into printouts. A printout ends on the page that says "Page N of N"."""
    printouts, current = [], []
    for page in pages:
        current.append(page)
        m = PAGE_COUNTER_RE.search(page["text"])
        if m and m.group(1) == m.group(2):
            printouts.append(current)
            current = []
    if current:  # A missing final counter should not lose pages.
        printouts.append(current)
    return printouts


def strip_boilerplate(text: str) -> list[str]:
    """Drop header, footer, page counter and blank lines. Returns the remaining lines."""
    kept = []
    for line in text.splitlines():
        if HEADER_RE.match(line) or FOOTER_RE.match(line):
            continue
        if PAGE_COUNTER_RE.fullmatch(line.strip()):
            continue
        if line.strip():
            kept.append(line.rstrip())
    return kept


def _is_footnote_start(line: str) -> str | None:
    """Return the footnote number if this line starts a footnote, else None."""
    m = FOOTNOTE_START_RE.match(line)
    if m and AMENDING_ACT_RE.search(line):
        return m.group(1)
    return None


def split_footnotes(
    page_lines: list[tuple[int, list[str]]],
) -> tuple[list[tuple[int, list[str]]], list[Footnote]]:
    """Cut the footnote block off the end of one printout.

    `page_lines` is [(page_no, lines)] for the printout. The block starts at the first
    footnote-style line whose number was also used as a marker earlier in the printout.
    Requiring the marker guards against a numbered body line that happens to mention an Act.
    """
    seen_markers: set[str] = set()
    cut: tuple[int, int] | None = None  # (index into page_lines, line index)
    for pi, (_, lines) in enumerate(page_lines):
        for li, line in enumerate(lines):
            number = _is_footnote_start(line)
            if number is not None and number in seen_markers:
                cut = (pi, li)
                break
            seen_markers.update(MARKER_RE.findall(line))
        if cut:
            break

    if cut is None:
        return page_lines, []

    # Body: everything before the cut. The page where the cut happens keeps its top part.
    body = page_lines[: cut[0]] + [(page_lines[cut[0]][0], page_lines[cut[0]][1][: cut[1]])]
    block = [(page_lines[cut[0]][0], page_lines[cut[0]][1][cut[1] :])] + page_lines[cut[0] + 1 :]
    # Pages that are only footnotes become empty pages; keep them so page numbers stay aligned.
    body += [(page_no, []) for page_no, _ in page_lines[cut[0] + 1 :]]

    footnotes: list[Footnote] = []
    for page_no, lines in block:
        for line in lines:
            number = _is_footnote_start(line)
            if number is not None:
                footnotes.append(Footnote(number=number, page=page_no, text=line.strip()))
            elif footnotes:  # Continuation line, usually the quoted old text.
                footnotes[-1].text += "\n" + line.strip()
    return body, footnotes


def _find_closing_bracket(text: str, open_pos: int) -> int | None:
    """Index of the "]" matching the "[" at open_pos, allowing nested brackets."""
    depth = 0
    for i in range(open_pos, len(text)):
        if text[i] == "[":
            depth += 1
        elif text[i] == "]":
            depth -= 1
            if depth == 0:
                return i
    return None


def remove_markers(text: str, numbers: set[str]) -> str:
    """Remove footnote markers whose number is in `numbers`.

    Only known footnote numbers are touched, so real brackets like "[Table: Sl. No. 1(i)]"
    are left alone.
    """
    out, pos = [], 0
    while True:
        m = next((m for m in MARKER_RE.finditer(text, pos) if m.group(1) in numbers), None)
        if m is None:
            out.append(text[pos:])
            return "".join(out)
        out.append(text[pos : m.start()])
        bracket = m.end() - 1
        close = _find_closing_bracket(text, bracket)
        if close is None:  # No partner: drop only the opener "25[".
            pos = m.end()
            continue
        inner = text[bracket + 1 : close]
        if inner.strip() == "***":
            # The text was deleted from the law. Say so, so the LLM can answer
            # "this was omitted" instead of seeing an empty item.
            out.append(OMITTED)
        else:
            # Keep inner text. Process it too, in case markers are nested.
            out.append(remove_markers(inner, numbers))
        pos = close + 1


def tidy_lines(lines: list[str]) -> list[str]:
    """Remove the page's common left margin and shrink long runs of spaces.

    Layout mode pads table columns with many spaces. Two spaces still show a column break
    and save room in each chunk. Relative indent is kept: it shows how clauses nest.
    """
    lines = [line for line in lines if line.strip()]
    if not lines:
        return []
    margin = min(len(line) - len(line.lstrip(" ")) for line in lines)
    tidied = []
    for line in lines:
        line = line[margin:]
        indent = len(line) - len(line.lstrip(" "))
        body = re.sub(r" {2,}", "  ", line.strip())
        tidied.append(" " * indent + body)
    return tidied


def clean_printout(printout: list[dict], strip_footnotes: bool = True) -> CleanResult:
    page_lines = [(p["page"], strip_boilerplate(p["text"])) for p in printout]
    footnotes: list[Footnote] = []
    if strip_footnotes:
        page_lines, footnotes = split_footnotes(page_lines)
        numbers = {f.number for f in footnotes}
        if numbers:
            joined = PAGE_BREAK.join("\n".join(lines) for _, lines in page_lines)
            joined = remove_markers(joined, numbers)
            page_texts = joined.split(PAGE_BREAK)
            page_lines = [(pn, t.split("\n")) for (pn, _), t in zip(page_lines, page_texts)]
    pages = [{"page": pn, "text": "\n".join(tidy_lines(lines))} for pn, lines in page_lines]
    return CleanResult(pages=pages, footnotes=footnotes)


def clean_pages(pages: list[dict], strip_footnotes: bool = True) -> CleanResult:
    """Clean every page. Set strip_footnotes=False for the footnote ablation."""
    result = CleanResult(pages=[])
    for printout in group_printouts(pages):
        part = clean_printout(printout, strip_footnotes)
        result.pages.extend(part.pages)
        result.footnotes.extend(part.footnotes)
    return result


def main() -> None:
    """Clean the cached pages and save the removed footnotes for review.

    Run: uv run python -m income_tax_agent.ingest.clean
    """
    import json
    from bisect import bisect_right

    from income_tax_agent.config import get_settings
    from income_tax_agent.ingest.extract import load_pages
    from income_tax_agent.ingest.sections import build_document

    settings = get_settings()
    pages = load_pages(settings.pages_path)
    result = clean_pages(pages, settings.strip_footnotes)
    doc = build_document(result.pages)

    out = settings.pages_path.parent / "footnotes_removed.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for fn in result.footnotes:
            # Footnotes sit at the end of their printout, so they belong to the section
            # that is open at the end of the footnote's page (or the last page before it,
            # if the page held only footnotes and is now empty).
            next_page = bisect_right(doc.page_numbers, fn.page)
            end = doc.page_offsets[next_page] - 1 if next_page < len(doc.page_offsets) else len(doc.text) - 1
            section = doc.section_at(end)
            record = {
                "number": fn.number,
                "page": fn.page,
                "section": section.number if section else None,
                "quotes_old_text": fn.quotes_old_text,
                "text": fn.text,
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    n_sections = sum(1 for s in doc.sections if not s.number.startswith("Schedule"))
    print(f"Pages: {len(result.pages)}  characters after cleaning: {len(doc.text):,}")
    print(f"Sections found: {n_sections}  schedules found: {len(doc.sections) - n_sections}")
    print(f"Footnotes removed: {len(result.footnotes)} "
          f"({sum(f.quotes_old_text for f in result.footnotes)} quote old text) -> {out}")


if __name__ == "__main__":
    main()
