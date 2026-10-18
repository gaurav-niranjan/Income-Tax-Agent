"""What flows through the answer graph."""

from typing import TypedDict

from income_tax_agent.retrieval.retriever import Hit


class AnswerState(TypedDict, total=False):
    # Input
    question: str
    mode: str  # retrieval mode: dense, bm25 or hybrid
    k: int  # number of chunks retrieved
    neighbours: bool  # also pass each hit's previous/next chunk from the same section
    expand: bool  # let an LLM add search queries in the Act's wording
    # Filled by the nodes
    queries: list[str]  # what was searched: the question first, then any expansions
    expand_error: str  # set when expansion failed and only the question was searched
    hits: list[Hit]
    answer: str
    refused: bool  # True when the answer is "I could not find this in the Act."
    citations: list[str]  # section numbers cited in the answer
    # Cited but not among the retrieved chunks: a sign the model used outside knowledge.
    unsupported_citations: list[str]
