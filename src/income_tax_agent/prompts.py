"""Prompts for answering from the Act. Changing them invalidates the LLM cache (on purpose)."""

import re

from income_tax_agent.retrieval.retriever import Hit

NOT_FOUND = "I could not find this in the Act."

# Rules 2 and 3 exist because one off-topic excerpt at the top made the model refuse:
# "tax laws for non-resident indians" got Section 160 (foreign tax relief) first and
# Sections 213, 216, 217 (the NRI rules) below it. Without 160 it answered (2026-10-24).
# Rule 11: "tax on a salary of 50 lakh?" was refused although Section 202's rate table was
# retrieved. The Act has rates, not totals, and nothing allowed a calculation (2026-10-29).
ANSWER_SYSTEM = f"""You answer questions about India's Income-tax Act, 2025, as amended by the Finance Act, 2026.

The numbered excerpts below are search results from the Act. Search is not perfect: some excerpts may be about something else, and the most useful one is not always first.

Rules:
1. Use ONLY the excerpts. Do not use outside knowledge, even if you are sure of it.
2. First decide which excerpts are relevant to the question. Answer from those. Ignore the others completely: do not mention them, and do not let them stop you from answering.
3. Reply with exactly "{NOT_FOUND}" and nothing else only if no excerpt is relevant. If the relevant excerpts answer only part of the question (common for broad questions such as "What are the rules for X?"), answer that part and end with one short sentence saying which part the excerpts do not cover.
4. Cite the source of every claim in square brackets, like [Section 202] or [Schedule XV]. Only cite sections named in the excerpt headers. Never cite excerpt numbers: they are not part of the Act.
5. The excerpts may define a different or narrower term than the one asked about (for example the same words with a qualifier such as "specified" or "eligible" added, or a meaning that applies only within one section). Then say so plainly: state which term the excerpts define and that it is not the general meaning asked about. Do not present it as the answer to the question.
6. The Act writes amounts in rupees, e.g. Rs. 1200000 is 12 lakh. Quote amounts as the Act gives them; you may add the lakh form in round brackets, e.g. Rs. 1200000 (12 lakh). Square brackets are only for citations.
7. Answer only what is asked. Leave out rules for other kinds of taxpayers or situations the question does not ask about.
8. Include every condition from the excerpts that changes the answer, such as a limit, an age or date, or who the rule applies to. A short answer that drops such a condition is wrong.
9. Start with a direct answer, then give the key conditions. Use plain English and keep it short.
10. Do not add a "not tax advice" disclaimer; the app shows one.
11. If the question asks for an amount you can work out from the excerpts (for example the tax on a given income, using a rate table), calculate it. Show each step with the rate and amount used, then the total. Then say briefly what the total leaves out because the excerpts do not cover it (for example surcharge, cess, or deductions that depend on the person's situation).

Answer in plain, simple English. The Act uses complicated legal language, so explain it simply."""


def _label(numbers: list[str]) -> str:
    """["202"] -> "Section 202"; ["201", "202"] -> "Sections 201, 202"; schedules kept as is."""
    sections = [n for n in numbers if not n.startswith("Schedule")]
    schedules = [n for n in numbers if n.startswith("Schedule")]
    parts = []
    if sections:
        parts.append(
            ("Section " if len(sections) == 1 else "Sections ") + ", ".join(sections)
        )
    parts += schedules
    return "; ".join(parts) or "unknown section"


def format_context(hits: list[Hit]) -> str:
    blocks = []
    # Numbered by position, not rank: neighbour chunks share their hit's rank.
    for n, h in enumerate(hits, start=1):
        c = h.chunk
        titles = "; ".join(t for t in c.section_titles if t)
        pages = ", ".join(map(str, c.pages))
        blocks.append(
            f"[Excerpt {n} | {_label(c.sections)} | {titles} | page {pages}]\n{c.text}"
        )
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


# "Excerpt 4", "Excerpts 1 and 2", "Excerpt 1 & Excerpt 2" (with any separator before it).
_EXCERPT_REF_RE = re.compile(
    r"\s*(?:[,;&]|\band\b)?\s*Excerpts?\s+\d+(?:\s*(?:,|&|and)\s*(?:Excerpt\s+)?\d+)*",
    re.IGNORECASE,
)


def strip_excerpt_refs(answer: str) -> str:
    """Remove excerpt numbers from square-bracket citations.

    The prompt forbids them, but the model still writes "[Section 126, Excerpt 4]".
    Excerpt numbers mean nothing to a reader, so drop them in code:
    "[Section 126, Excerpt 4]" -> "[Section 126]"; "[Excerpt 2]" -> removed.
    """

    def clean(m: re.Match) -> str:
        inner = _EXCERPT_REF_RE.sub("", m.group(1)).strip(" ,;&")
        inner = re.sub(r"^(?:and)\s+|\s+(?:and)$", "", inner)
        return f"[{inner}]" if inner else ""

    cleaned = re.sub(r"\[([^\]]*Excerpt[^\]]*)\]", clean, answer, flags=re.IGNORECASE)
    # A removed bracket can leave "word ." or a double space behind.
    return re.sub(r"[ \t]+([.,;:])", r"\1", re.sub(r"[ \t]{2,}", " ", cleaned))


# --- Query expansion ---
# The model writes extra search queries; the answer prompt above never sees them. So the
# model's outside knowledge can change *which* chunks are found, not what the answer says.

EXPAND_N = 3  # the prompt asks for exactly this many (one per style in rule 5)

# The example is deliberately not about any eval question, so it cannot inflate the numbers.
EXPAND_SYSTEM = f"""You help search India's Income-tax Act, 2025. You turn a user's question into search queries that use the Act's own wording. You do not answer the question.

Write exactly {EXPAND_N} search queries, one per line. No numbering, bullets, quotes or other text.

Rules:
1. Use the Act's terms, not everyday words. Examples: "tax year" (the Act has no "assessment year" or "financial year"), "tax deducted at source", "tax collected at source", "total income", "assessee", "resident in India".
2. Spell out abbreviations: TDS, TCS, HUF (Hindu undivided family), LRS (Liberalised Remittance Scheme), PF (provident fund), HRA (house rent allowance).
3. Write amounts in rupees as the Act does: digits, no commas. 12 lakh = Rs. 1200000, 1.5 crore = Rs. 15000000.
4. Do not add section numbers. The Act was renumbered in 2025, so numbers from the old Income-tax Act, 1961 (such as 80C or 115BAC) point to the wrong place. If the question uses an old number, describe what that provision is about instead.
5. Make the {EXPAND_N} queries different:
   - line 1: key terms only, like a keyword search;
   - line 2: a sentence written the way the Act would write it, e.g. a definition ('"X" means ...') or a rule ('... shall be allowed a deduction of ...');
   - line 3: the question rephrased in plain English with the Act's terms.
6. Each query must make sense on its own and be under 30 words.

Example
Question: I made a business loss of 3 lakh this year. Can I use it next year?
loss profits and gains of business or profession carried forward set off following tax year
Where the loss under the head "Profits and gains of business or profession" of Rs. 300000 is not wholly set off, it shall be carried forward to the following tax year
Can a loss of Rs. 300000 from business be carried forward and set off against income of a later tax year"""


def expand_user_prompt(question: str) -> str:
    return f"Question: {question}"


# "- ", "* ", "• ", "1. ", "2) ", "Line 1: ". The lookahead keeps "1.25 lakh" intact.
_LIST_MARK_RE = re.compile(r"^\s*(?:[-*•]|\d+[.)](?=\s)|line \d+:)\s*", re.IGNORECASE)


def parse_expansions(raw: str, question: str, n: int = EXPAND_N) -> list[str]:
    """The model's reply -> up to n extra queries.

    Models add list marks, wrap lines in quotes, or start with "Here are 3 queries:"
    despite the prompt. Drop those, blank lines and repeats of the question.
    """
    seen = {question.strip().casefold()}
    out: list[str] = []
    for line in raw.splitlines():
        q = _LIST_MARK_RE.sub("", line).strip()
        # Only strip a matching pair: '"senior citizen" means ...' keeps its quotes.
        if len(q) > 1 and q[0] == q[-1] and q[0] in "\"'`":
            q = q[1:-1].strip()
        if not q or q.endswith(":") or q.casefold() in seen:
            continue
        seen.add(q.casefold())
        out.append(q)
    return out[:n]


# --- Follow-up questions (chat memory) ---
# Search needs a question that makes sense on its own: "And for senior citizens?" finds
# nothing useful. So a follow-up is rewritten using the earlier turns, and the rewrite is
# searched and answered like a first question. The answer prompt never sees the history,
# so a single-turn question gets exactly the same prompts (and cache hits) as before.

HISTORY_ANSWER_CHARS = 600  # earlier answers are cut to this: enough to resolve "that", "it"

REWRITE_SYSTEM = """You help with a chat about India's Income-tax Act, 2025. You rewrite the user's latest question so that it makes sense without the conversation. You do not answer it.

Rules:
1. Replace words that point back to the conversation ("it", "that", "this deduction", "what about ...", "and for ...") with what they refer to.
2. If the question already makes sense on its own, return it unchanged.
3. Keep the user's own words and amounts. Do not add section numbers or facts that are not in the conversation.
4. Reply with only the rewritten question, on one line."""


def rewrite_user_prompt(question: str, history: list[dict]) -> str:
    turns = []
    for turn in history:
        answer = turn["answer"]
        if len(answer) > HISTORY_ANSWER_CHARS:
            answer = answer[:HISTORY_ANSWER_CHARS] + "..."
        turns.append(f"User: {turn['question']}\nAssistant: {answer}")
    return "Earlier in the conversation:\n\n" + "\n\n".join(turns) + f"\n\nFollow-up question: {question}"


def parse_rewrite(raw: str, question: str) -> str:
    """The first non-empty line, without wrapping quotes; the question itself if there is none."""
    for line in raw.splitlines():
        q = line.strip()
        if len(q) > 1 and q[0] == q[-1] and q[0] in "\"'`":
            q = q[1:-1].strip()
        if q:
            return q
    return question


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
