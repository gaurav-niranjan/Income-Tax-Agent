"""What flows through the answer graph."""

from typing import TypedDict

from income_tax_agent.retrieval.retriever import Hit


class AnswerState(TypedDict, total=False):
    # Input
    question: str
    mode: str  # retrieval mode: dense, bm25 or hybrid
    k: int  # number of chunks retrieved
    neighbours: bool  # also pass each hit's previous/next chunk from the same section
    # Filled by the nodes
    hits: list[Hit]
    answer: str
    refused: bool  # True when the answer is "I could not find this in the Act."
    citations: list[str]  # section numbers cited in the answer
    # Cited but not among the retrieved chunks: a sign the model used outside knowledge.
    unsupported_citations: list[str]
