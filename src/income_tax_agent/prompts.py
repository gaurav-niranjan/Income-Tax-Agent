"""Prompts for answering from the Act. Changing them invalidates the LLM cache (on purpose)."""

import re

from income_tax_agent.retrieval.retriever import Hit

NOT_FOUND = "I could not find this in the Act."

ANSWER_SYSTEM = f"""You answer questions about India's Income-tax Act, 2025, as amended by the Finance Act, 2026.

Rules:
1. Use ONLY the numbered excerpts from the Act given below. Do not use outside knowledge, even if you are sure of it.
2. Cite the source of every claim in square brackets, like [Section 202] or [Schedule XV]. Only cite sections named in the excerpt headers.
3. If the excerpts do not contain the answer, reply with exactly: "{NOT_FOUND}" and nothing else.
4. The Act writes amounts in rupees, e.g. Rs. 1200000 is 12 lakh. Quote amounts as the Act gives them; you may add the lakh form in round brackets, e.g. Rs. 1200000 (12 lakh). Square brackets are only for citations.
5. Answer only what is asked. Leave out rules for other kinds of taxpayers or situations the question does not ask about.
6. If a table or list you rely on looks cut off (it stops at an excerpt's edge, or rows are missing), give what the excerpts show and say clearly: "This may be incomplete: the excerpts show only part of the table."
7. Start with a direct answer, then give the key conditions. Use plain English and keep it short.
8. Do not add a "not tax advice" disclaimer; the app shows one."""


def _label(numbers: list[str]) -> str:
    """["202"] -> "Section 202"; ["201", "202"] -> "Sections 201, 202"; schedules kept as is."""
    sections = [n for n in numbers if not n.startswith("Schedule")]
    schedules = [n for n in numbers if n.startswith("Schedule")]
    parts = []
    if sections:
        parts.append(("Section " if len(sections) == 1 else "Sections ") + ", ".join(sections))
    parts += schedules
    return "; ".join(parts) or "unknown section"


def format_context(hits: list[Hit]) -> str:
    blocks = []
    # Numbered by position, not rank: neighbour chunks share their hit's rank.
    for n, h in enumerate(hits, start=1):
        c = h.chunk
        titles = "; ".join(t for t in c.section_titles if t)
        pages = ", ".join(map(str, c.pages))
        blocks.append(f"[Excerpt {n} | {_label(c.sections)} | {titles} | page {pages}]\n{c.text}")
    return "\n\n".join(blocks)


def answer_user_prompt(question: str, hits: list[Hit]) -> str:
    return f"Excerpts from the Act:\n\n{format_context(hits)}\n\nQuestion: {question}"


# Citations look like "[Section 202]", "[Section 202(1)(a)]", "[Sections 202 and 156]",
# "[Schedule XV]" or "[Section 393(1), Table: Sl. No. 2(ii)]".
CITATION_RE = re.compile(r"\[[^\]]*(?:Section|Schedule)[^\]]*\]")
# A number with optional sub-section parts: "202", "202(1)(a)".
_NUM = r"\d+(?:\([^)]*\))*"
# "Section 202" or "Sections 202, 203 and 156": only numbers right after the word count,
# so "Sl. No. 2(ii)" in the same bracket is not read as Section 2.
SECTION_LIST_RE = re.compile(rf"Sections?\s+({_NUM}(?:\s*(?:,|and|&)\s*{_NUM})*)")
SCHEDULE_RE = re.compile(r"Schedule ([IVXL]+)\b")


def parse_citations(answer: str) -> list[str]:
    """Section numbers cited in the answer, in order, without duplicates.

    "[Section 202(1)]" -> "202": "(1)" is a sub-section, not a section.
    """
    found: list[str] = []
    for bracket in CITATION_RE.findall(answer):
        for number_list in SECTION_LIST_RE.findall(bracket):
            found += re.findall(r"(\d+)(?:\([^)]*\))*", number_list)
        found += [f"Schedule {r}" for r in SCHEDULE_RE.findall(bracket)]
    return list(dict.fromkeys(found))
