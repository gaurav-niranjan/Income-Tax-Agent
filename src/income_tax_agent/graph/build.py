"""Wire the answer graph:

    START -> expand -> retrieve --(chunks found)--> generate --> END
                                \\--(no chunks)----> not_found --> END

`expand` adds LLM-written search queries when the state's `expand` flag is on;
otherwise it passes the question through unchanged.
Later phases add nodes here (grade-and-retry, verify) without changing callers.
"""

from functools import partial

from langgraph.graph import END, START, StateGraph

from income_tax_agent.config import Settings, get_settings
from income_tax_agent.graph import nodes
from income_tax_agent.graph.state import AnswerState
from income_tax_agent.llm import LLM, get_expand_llm, get_llm
from income_tax_agent.retrieval.retriever import Retriever, get_retriever


def build_graph(retriever: Retriever, llm: LLM, expand_llm: LLM | None = None):
    """expand_llm writes the search queries; None = use the answer model."""
    graph = StateGraph(AnswerState)
    graph.add_node("expand", partial(nodes.expand, llm=expand_llm or llm))
    graph.add_node("retrieve", partial(nodes.retrieve, retriever=retriever))
    graph.add_node("generate", partial(nodes.generate, llm=llm))
    graph.add_node("not_found", nodes.not_found)
    graph.add_edge(START, "expand")
    graph.add_edge("expand", "retrieve")
    graph.add_conditional_edges("retrieve", nodes.route_after_retrieve, ["generate", "not_found"])
    graph.add_edge("generate", END)
    graph.add_edge("not_found", END)
    return graph.compile()


def answer_question(
    question: str,
    mode: str | None = None,
    k: int | None = None,
    neighbours: bool | None = None,
    expand: bool | None = None,
    graph=None,
    settings: Settings | None = None,
) -> AnswerState:
    """Answer one question with the default index, retrieval settings and LLMs."""
    settings = settings or get_settings()
    if graph is None:
        graph = build_graph(get_retriever(settings.index_name), get_llm(settings), get_expand_llm(settings))
    return graph.invoke(
        {
            "question": question,
            "mode": mode or settings.answer_mode,
            "k": k or settings.answer_k,
            "neighbours": settings.answer_neighbours if neighbours is None else neighbours,
            "expand": settings.expand_queries if expand is None else expand,
        }
    )
