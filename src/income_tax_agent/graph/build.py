"""Wire the answer graph:

    START -> rewrite -> expand -> retrieve --(chunks found)--> generate --> END
                                          \\--(no chunks)----> not_found --> END

`rewrite` turns a follow-up into a standalone question using the chat history (only
when there is history; the eval's single questions pass through unchanged).
`expand` adds LLM-written search queries when the state's `expand` flag is on;
otherwise it passes the question through unchanged.
Later phases add nodes here (grade-and-retry, verify) without changing callers.

Pass a checkpointer (e.g. InMemorySaver) to keep each chat's history between questions;
every `invoke` then needs `config={"configurable": {"thread_id": ...}}`.
"""

from functools import partial

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.graph import END, START, StateGraph

from income_tax_agent.config import Settings, get_settings
from income_tax_agent.graph import nodes
from income_tax_agent.graph.state import AnswerState
from income_tax_agent.llm import LLM, get_expand_llm, get_llm
from income_tax_agent.retrieval.retriever import Retriever, get_retriever


def memory_checkpointer() -> InMemorySaver:
    """Keeps every chat in RAM until the process restarts.

    The serializer is told our state's dataclasses are safe to load back; LangGraph warns
    about (and will later block) types it was not told about.
    """
    serde = JsonPlusSerializer(
        allowed_msgpack_modules=[
            ("income_tax_agent.retrieval.retriever", "Hit"),
            ("income_tax_agent.ingest.chunkers.base", "Chunk"),
        ]
    )
    return InMemorySaver(serde=serde)


def build_graph(
    retriever: Retriever,
    llm: LLM,
    expand_llm: LLM | None = None,
    checkpointer: BaseCheckpointSaver | None = None,
    history_turns: int | None = None,
):
    """expand_llm writes the search queries and rewrites follow-ups; None = use the answer model."""
    if history_turns is None:
        history_turns = get_settings().history_turns
    graph = StateGraph(AnswerState)
    graph.add_node(
        "rewrite",
        partial(nodes.rewrite, llm=expand_llm or llm, history_turns=history_turns),
    )
    graph.add_node("expand", partial(nodes.expand, llm=expand_llm or llm))
    graph.add_node("retrieve", partial(nodes.retrieve, retriever=retriever))
    graph.add_node("generate", partial(nodes.generate, llm=llm))
    graph.add_node("not_found", nodes.not_found)
    graph.add_edge(START, "rewrite")
    graph.add_edge("rewrite", "expand")
    graph.add_edge("expand", "retrieve")
    graph.add_conditional_edges(
        "retrieve", nodes.route_after_retrieve, ["generate", "not_found"]
    )
    graph.add_edge("generate", END)
    graph.add_edge("not_found", END)
    return graph.compile(checkpointer=checkpointer)


def answer_question(
    question: str,
    mode: str | None = None,
    k: int | None = None,
    neighbours: bool | None = None,
    expand: bool | None = None,
    rerank: bool | None = None,
    graph=None,
    settings: Settings | None = None,
) -> AnswerState:
    """Answer one question with the default index, retrieval settings and LLMs."""
    settings = settings or get_settings()
    if graph is None:
        graph = build_graph(
            get_retriever(settings.index_name),
            get_llm(settings),
            get_expand_llm(settings),
        )
    return graph.invoke(
        {
            "question": question,
            "mode": mode or settings.answer_mode,
            "k": k or settings.answer_k,
            "neighbours": (
                settings.answer_neighbours if neighbours is None else neighbours
            ),
            "expand": settings.expand_queries if expand is None else expand,
            "rerank": settings.rerank if rerank is None else rerank,
        }
    )
