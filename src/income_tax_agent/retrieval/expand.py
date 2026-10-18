"""Query expansion: an LLM writes extra search queries in the Act's own wording.

Users say "TDS", "12 lakh" or "money sent abroad"; the Act says "tax deducted at source",
"Rs. 1200000" and "Liberalised Remittance Scheme". The original question is always the
first query, so a bad expansion adds noise but cannot lose what the user asked.
The retriever searches with every query and merges the lists (Retriever.retrieve_multi).
"""

from income_tax_agent.llm import LLM
from income_tax_agent.prompts import EXPAND_SYSTEM, expand_user_prompt, parse_expansions


def expand_query(question: str, llm: LLM) -> list[str]:
    """[question, *extra queries]. API errors are raised; the caller decides how to fall back."""
    raw = llm.complete(EXPAND_SYSTEM, expand_user_prompt(question))
    return [question, *parse_expansions(raw, question)]
