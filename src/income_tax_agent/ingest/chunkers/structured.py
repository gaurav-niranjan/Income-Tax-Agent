"""Structure-aware chunker: cut where the Act itself is cut, not every N characters.

Rules, from most to least important:

1. Never cross a section (or Schedule) boundary.
2. A section that fits in `max_chars` is one chunk.
3. A bigger section is split into items: sub-sections "(1)", "(2)", ..., table header,
   table rows "1.", "2." (or "(1)" in a few tables), table notes, and in Schedules the
   paragraphs "1.", "2.". Consecutive items are packed together up to `max_chars`.
4. Each definition in a long section (Section 2: `(100) "senior citizen" means ...`) gets
   its own chunk, so one chunk is about one term.
5. A chunk that starts in the middle of a table repeats the table's header (column names),
   so a row like "3. From Rs. 800001 to Rs. 1200000  10%" still says what its columns mean.
6. An item bigger than `max_chars` is split at clause starts "(a)", "(i)", else at lines.
7. A chunk smaller than `min_chars` is merged into the one before it (same section), if
   the result is not much bigger than `max_chars`.

Every chunk gets a search prefix like "Section 393(1) Table, Sl. No. 2 to 4: Tax to be
deducted at source." The LLM sees the plain text.

Sizes are counted without whitespace runs (len of " ".join(text.split())), because layout
text pads table columns with spaces that BGE does not turn into tokens.
"""

import re
from dataclasses import dataclass

from income_tax_agent.ingest.chunkers.base import Chunk
from income_tax_agent.ingest.sections import Document, SectionStart

# "(4) Nothing contained ...", "(1)(a) Every person ...", "(1A) ...". Sub-section numbers
# sit at the start of a line; Section 2 right-aligns them, so allow up to 3 spaces.
SUBSECTION_RE = re.compile(r"^ {0,3}\((\d+)([A-Z]*)\)(?=[\s(]|$)")
# The first sub-section shares the number line: "202. (1) Irrespective ...".
FIRST_SUBSECTION = r"^\s*{number}\s*\.\s*\((\d+)([A-Z]*)\)(?=[\s(]|$)"
# A wrapped line that starts with a reference, e.g. "... under sub-section\n(2) shall ...",
# looks like a sub-section start. The word before the line break gives it away.
REFERENCE_END_RE = re.compile(r"(sub-sections?|sections?|clauses?|and|or|of|to|in|under|with|,)$")
# A gap in numbering (an omitted sub-section) needs the line before to end a sentence.
SENTENCE_END_RE = re.compile(r"[.;:—–-]$")
# Each definition starts with its term in quotes: `(100) "senior citizen" means`.
DEFINITION_RE = re.compile(r'^\s*\(\d+[A-Z]*\)\s*(\([a-z]\)\s*)?"')

TABLE_RE = re.compile(r"^\s*TABLE\s*$")
DOT_ROW_RE = re.compile(r"^ {0,10}(\d+)([A-Z]*)\.(?=\s)")  # "1.  Upto Rs. 400000", "38A. ..."
PAREN_ROW_RE = re.compile(r"^ {0,3}\((\d+)([A-Z]*)\)(?=[\s(])")  # Section 206's table
NOTE_RE = re.compile(r"^\s*(Notes?|Explanation)\b[^—–]{0,12}[—–]")  # "Note 1.—", "Explanation.—"
PART_RE = re.compile(r"^\s*PART [A-Z]+\s*$")
PARAGRAPH_RE = re.compile(r"^ ?(\d+)([A-Z]*)\.(?=\s)")  # Schedule paragraphs: "1. For any ..."
# Places to cut an oversized item: clause or sub-clause starts, provisos, explanations.
CLAUSE_RE = re.compile(r"^\s*(\(([a-z]{1,5}|[A-Z])\)|Provided\b|Explanation\b)")

MAX_HEADER_CHARS = 400  # A longer "header" means no numbered rows were found; don't repeat it.


def size(text: str) -> int:
    return len(" ".join(text.split()))


@dataclass
class Item:
    """A structural piece of one section, as a span of Document.text."""

    start: int
    end: int
    ref: str  # "(4)", "(1) Table, Sl. No. 5", "paragraph 2", "" for the opening text
    kind: str  # "text", "definition", "table_header", "row"
    table: int | None = None  # for rows: index of their table's header item


def _number_ok(n: int, suffix: str, last: tuple[int, str], prev_line: str) -> bool:
    """Is "(n)" the next sub-section after `last`, judging by numbering and the line before?"""
    last_n, last_suffix = last
    prev = prev_line.rstrip()
    if n == last_n and suffix > last_suffix:  # "(1A)" after "(1)"
        return not REFERENCE_END_RE.search(prev)
    if n == last_n + 1 and not suffix:
        return not REFERENCE_END_RE.search(prev)
    if n > last_n + 1:  # a gap: only after a full stop, semicolon, colon or dash
        return bool(SENTENCE_END_RE.search(prev))
    return False


def split_items(text: str, base: int, number: str) -> list[Item]:
    """Split one section's text (starting at offset `base` in the document) into items.

    `number` is the section number ("202") or "Schedule III".
    """
    is_schedule = number.startswith("Schedule")
    first_re = re.compile(FIRST_SUBSECTION.format(number=re.escape(number)))
    starts: list[tuple[int, str, str, int | None]] = [(0, "", "text", None)]  # (offset, ref, kind, table)
    last_sub = (0, "")
    last_para = (0, "")
    sub_ref = ""
    table: int | None = None  # index into `starts` of the current table's header
    row_style: str | None = None  # "dot" or "paren", fixed by the table's first row
    last_row = (0, "")
    offset = 0
    lines = text.split("\n")
    for j, line in enumerate(lines):
        prev = lines[j - 1] if j else ""
        new: tuple[str, str, int | None] | None = None  # (ref, kind, table)

        if TABLE_RE.match(line):
            row_style, last_row = None, (0, "")
            new = (f"{sub_ref} Table".strip(), "table_header", None)
        elif table is not None and (row := _table_row(line, row_style, last_row)):
            style, n, suffix = row
            row_style, last_row = style, (n, suffix)
            new = (f"{sub_ref} Table, Sl. No. {n}{suffix}".strip(), "row", table)
        elif table is not None and last_row[0] and NOTE_RE.match(line):
            new = (f"{sub_ref} Table, Note".strip(), "row", table)  # notes travel with rows
        elif not is_schedule:
            first = first_re.match(line) if not last_sub[0] else None
            m = first or SUBSECTION_RE.match(line)
            # On the number line, the "line before" is the title: no reference check.
            if m and _number_ok(int(m.group(1)), m.group(2), last_sub, "." if first else prev):
                last_sub = (int(m.group(1)), m.group(2))
                sub_ref = f"({m.group(1)}{m.group(2)})"
                table = None
                new = (sub_ref, "definition" if DEFINITION_RE.match(line) else "text", None)
        elif PART_RE.match(line):
            last_para, table, sub_ref = (0, ""), None, line.strip().title()  # "Part A"
            new = (sub_ref, "text", None)
        elif table is None and (m := PARAGRAPH_RE.match(line)):
            if _number_ok(int(m.group(1)), m.group(2), last_para, prev):
                last_para = (int(m.group(1)), m.group(2))
                new = (f"{sub_ref} paragraph {m.group(1)}{m.group(2)}".strip(), "text", None)

        if new and offset > starts[-1][0]:
            starts.append((offset, *new))
        elif new:  # nothing since the last start (e.g. a section that opens with its table)
            starts[-1] = (offset, *new)
        if new and new[1] == "table_header":
            table = len(starts) - 1
        offset += len(line) + 1

    items = []
    for i, (start, ref, kind, tbl) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(text)
        items.append(Item(base + start, base + end, ref, kind, tbl))
    return items


def _table_row(line: str, style: str | None, last: tuple[int, str]) -> tuple[str, int, str] | None:
    """(style, number, suffix) if the line starts the table's next row, else None."""
    for name, regex in (("dot", DOT_ROW_RE), ("paren", PAREN_ROW_RE)):
        if style not in (None, name):
            continue
        m = regex.match(line)
        if not m:
            continue
        n, suffix = int(m.group(1)), m.group(2)
        if (n == last[0] + 1 and not suffix) or (n == last[0] and suffix > last[1]):
            return name, n, suffix
    return None


@dataclass
class StructuredChunker:
    max_chars: int = 1500
    min_chars: int = 300

    @property
    def name(self) -> str:
        return f"structured-{self.max_chars}"

    def config(self) -> dict:
        return {
            "type": "structured",
            "max_chars": self.max_chars,
            "min_chars": self.min_chars,
            "size_measure": "characters, whitespace runs collapsed",
            "search_prefix": "section + sub-section/table-row label + title (dense + bm25)",
        }

    # --- splitting -------------------------------------------------------------------

    def _split_big(self, doc: Document, item: Item) -> list[Item]:
        """Cut an item over max_chars at clause starts, else at line breaks."""
        if size(doc.text[item.start : item.end]) <= self.max_chars:
            return [item]
        pieces: list[Item] = []
        cur, last_clause = item.start, None
        pos = item.start
        for line in doc.text[item.start : item.end].split("\n"):
            line_end = min(pos + len(line) + 1, item.end)
            if pos > cur and size(doc.text[cur:line_end]) > self.max_chars:
                use_clause = last_clause and size(doc.text[cur:last_clause]) >= self.min_chars
                cut = last_clause if use_clause else pos
                pieces.append(Item(cur, cut, item.ref, item.kind, item.table))
                cur, last_clause = cut, None
            if pos > cur and CLAUSE_RE.match(line):
                last_clause = pos
            pos = line_end
        pieces.append(Item(cur, item.end, item.ref, item.kind, item.table))
        return pieces

    # --- packing ---------------------------------------------------------------------

    def _header_text(self, doc: Document, items: list[Item], group: list[Item]) -> str:
        """The table header to repeat, if the group starts inside a table without it."""
        first = group[0]
        if first.kind != "row" or first.table is None:
            return ""
        header = items[first.table]
        if any(p.start == header.start for p in group):
            return ""
        text = doc.text[header.start : header.end].strip("\n")
        return text if size(text) <= MAX_HEADER_CHARS else ""

    def _group_size(self, doc: Document, items: list[Item], group: list[Item]) -> int:
        body = doc.text[group[0].start : group[-1].end]
        return size(self._header_text(doc, items, group) + "\n" + body)

    @staticmethod
    def _compatible(group: list[Item], piece: Item) -> bool:
        """Definitions stand alone. Only the section's opening text may join one."""
        if piece.kind == "definition":
            return all(p.ref == "" for p in group)
        return not any(p.kind == "definition" for p in group)

    def _pack(self, doc: Document, items: list[Item]) -> list[list[Item]]:
        pieces = [p for item in items for p in self._split_big(doc, item)]
        groups: list[list[Item]] = []
        for p in pieces:
            if groups and self._compatible(groups[-1], p):
                if self._group_size(doc, items, groups[-1] + [p]) <= self.max_chars:
                    groups[-1].append(p)
                    continue
            groups.append([p])
        # Fold small groups into the one before, allowing a little over max_chars.
        merged: list[list[Item]] = []
        for g in groups:
            if merged and self._small(g, doc, items) and self._can_join(merged[-1], g, doc, items):
                merged[-1].extend(g)
            else:
                merged.append(g)
        # A small first group (often just the title line) has nothing before it: join the next.
        if len(merged) > 1 and self._small(merged[0], doc, items) and self._can_join(merged[0], merged[1], doc, items):
            merged[1] = merged[0] + merged[1]
            del merged[0]
        return merged

    def _small(self, group: list[Item], doc: Document, items: list[Item]) -> bool:
        return self._group_size(doc, items, group) < self.min_chars

    def _can_join(self, a: list[Item], b: list[Item], doc: Document, items: list[Item]) -> bool:
        """Can group b follow group a in one chunk? Allows up to 25% over max_chars."""
        ok = all(self._compatible(a + b[:i], p) for i, p in enumerate(b))
        return ok and self._group_size(doc, items, a + b) <= self.max_chars * 1.25

    # --- chunks ----------------------------------------------------------------------

    @staticmethod
    def _label(section: SectionStart, group: list[Item]) -> str:
        """ "Section 202(1) to (3)", "Section 393(1) Table, Sl. No. 2 to 4", "Schedule III"."""
        name = section.number if section.number.startswith("Schedule") else f"Section {section.number}"
        # Notes are not a place in the table worth naming, unless that is all there is.
        refs = [p.ref for p in group if p.ref and not p.ref.endswith("Note")] or [
            p.ref for p in group if p.ref
        ]
        if not refs:
            return name
        first, last = refs[0], refs[-1]
        sep = "" if first.startswith("(") else " "
        # "(1)" then rows of its own table: "(1) Table, Sl. No. 7" is still inside "(1)".
        if first == last or (last.startswith(first) and last[len(first)] in " ,"):
            return f"{name}{sep}{first}"
        # Drop the words both ends share: "(1) Table, Sl. No. 2" to "4", not to "(1) Table, Sl. No. 4".
        common = 0
        while common < min(len(first), len(last)) and first[common] == last[common]:
            common += 1
        cut = last.rfind(" ", 0, common + 1) + 1
        return f"{name}{sep}{first} to {last[cut:]}"

    def chunk(self, doc: Document) -> list[Chunk]:
        chunks: list[Chunk] = []
        bounds = [s.offset for s in doc.sections] + [len(doc.text)]
        for i, section in enumerate(doc.sections):
            # The Act's title page sits before Section 1; keep it with Section 1.
            start, end = (0 if i == 0 else bounds[i]), bounds[i + 1]
            text = doc.text[start:end]
            if not text.strip():
                continue
            if size(text) <= self.max_chars:
                groups = [[Item(start, end, "", "text")]]
                items = groups[0]
            else:
                items = split_items(text, start, section.number)
                groups = self._pack(doc, items)
            for group in groups:
                g_start, g_end = group[0].start, group[-1].end
                body = doc.text[g_start:g_end].strip()
                if not body:
                    continue
                header = self._header_text(doc, items, group)
                label = self._label(section, group)
                title = f": {section.title}" if section.title else ""
                chunks.append(
                    Chunk(
                        chunk_id=f"{self.name}:{len(chunks):06d}",
                        text=f"{header}\n{body}" if header else body,
                        pages=doc.pages_between(g_start, g_end),
                        sections=[section.number],
                        section_titles=[section.title],
                        extra={
                            "start": g_start,
                            "end": g_end,
                            "label": label,
                            "kinds": sorted({p.kind for p in group}),
                            "repeated_header": bool(header),
                            "section_chars": doc.section_chars_between(g_start, g_end),
                            "search_prefix": f"{label}{title}\n",
                        },
                    )
                )
        return chunks
