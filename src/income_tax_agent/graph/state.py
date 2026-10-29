"""What flows through the answer graph.

With a checkpointer (the app), the state of one chat (thread) is kept between questions.
Every per-question key is therefore written again on each run, so nothing from the
previous question is left behind. Only `history` grows.
"""

import operator
from typing import Annotated, TypedDict

from income_tax_agent.retrieval.retriever import Hit


class AnswerState(TypedDict, total=False):
    # Input
    question: str
    mode: str  # retrieval mode: dense, bm25 or hybrid
    k: int  # number of chunks retrieved
    neighbours: bool  # also pass each hit's previous/next chunk from the same section
    expand: bool  # let an LLM add search queries in the Act's wording
    rerank: bool  # reorder candidates with the cross-encoder; unset = settings.rerank
    # Filled by the nodes
    # The question rewritten to make sense without the chat; = question when there is no history.
    standalone_question: str
    rewrite_error: str | None  # set when the rewrite failed and the question was used as is
    queries: list[str]  # what was searched: the standalone question first, then any expansions
    expand_error: str | None  # set when expansion failed and only the question was searched
    hits: list[Hit]
    answer: str
    refused: bool  # True when the answer is "I could not find this in the Act."
    citations: list[str]  # section numbers cited in the answer
    # Cited but not among the retrieved chunks: a sign the model used outside knowledge.
    unsupported_citations: list[str]
    # Chat memory: one {"question", "answer"} per finished turn. The reducer appends.
    history: Annotated[list[dict], operator.add]
