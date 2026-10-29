"""Chat with the Income-tax Act, 2025. Answers come only from the Act, with sources.

Run locally:  uv run streamlit run app/streamlit_app.py
On Streamlit Community Cloud, put GOOGLE_API_KEY and the model names in the app's Secrets.
With DEV_MODE=1 in .env, each answer also shows timings, tokens, prompts and chat memory.
"""

import hashlib
import json
import math
import os
import time
import uuid

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

st.set_page_config(page_title="Income Tax Act Q&A", page_icon="📘", layout="centered")


def _secrets_to_env() -> None:
    """Streamlit Cloud keeps keys in st.secrets; our settings read environment variables."""
    try:
        for key, value in st.secrets.items():
            if isinstance(value, str):
                os.environ.setdefault(key.upper(), value)
    except (StreamlitSecretNotFoundError, FileNotFoundError):
        pass  # Running locally without secrets.toml: settings come from .env.


_secrets_to_env()

# Imported after the secrets are in the environment, because settings are read once.
from income_tax_agent.config import get_settings  # noqa: E402
from income_tax_agent.graph.build import build_graph, memory_checkpointer  # noqa: E402
from income_tax_agent.limits import QuestionLimits  # noqa: E402
from income_tax_agent.llm import (  # noqa: E402
    NotRetryable, QuotaExhausted, get_expand_llm, get_llm, record_llm_calls,
)
from income_tax_agent.retrieval.retriever import Retriever  # noqa: E402

MODE_LABELS = {
    "dense": "Meaning (embeddings)",
    "hybrid": "Meaning + keywords",
    "bm25": "Keywords only",
}
EXAMPLES = [
    "What are the income tax rates under the new regime?",
    "How many days must I stay in India to count as a resident?",
    "What is the GST rate on restaurant food?",
]

settings = get_settings()


def available_indexes() -> list[str]:
    """Index folders on disk, the configured default first. A folder counts once it has a manifest."""
    found = sorted(p.parent.name for p in settings.index_dir.glob("*/manifest.json"))
    return sorted(found, key=lambda name: name != settings.index_name)


def index_label(name: str) -> str:
    """A plain description for visitors, e.g. "Structured chunks (experiment)", from the manifest."""
    try:
        chunker = json.loads((settings.index_dir / name / "manifest.json").read_text())["chunker"]
    except (OSError, ValueError, KeyError):
        return name
    if chunker.get("type") == "structured":
        label = "Structured chunks: sections, sub-sections, table rows"
    elif chunker.get("type") == "fixed":
        label = f"Fixed {chunker['size']:,}-character chunks" if "size" in chunker else "Fixed-size chunks"
        label += " + section titles" if chunker.get("search_prefix") else ""
    else:
        label = name
    return label + (" (default)" if name == settings.index_name else " (experiment)")


@st.cache_resource
def chat_memory():
    """One store for all chats, each under its visitor's thread id. Lives in RAM, so a server
    restart forgets everything. Shared by every index, so switching index keeps the chat."""
    return memory_checkpointer()


@st.cache_resource
def question_limits() -> QuestionLimits:
    """One counter for all browser sessions, so reloading the page doesn't reset it."""
    return QuestionLimits(settings.max_questions_per_visitor, settings.max_questions_total,
                          settings.question_window_hours * 3600)


def visitor_id() -> str:
    """The visitor's IP address. Behind a proxy (Streamlit Cloud) the connection comes from the
    proxy, which puts the visitor's IP first in X-Forwarded-For. A custom client could fake that
    header; the cap for all visitors still holds."""
    forwarded = st.context.headers.get("X-Forwarded-For", "")
    ip = st.context.ip_address  # None on localhost; a mock object in AppTest
    return forwarded.split(",")[0].strip() or (ip if isinstance(ip, str) else "local")


def wait_text(seconds: float) -> str:
    hours, minutes = divmod(math.ceil(seconds / 60), 60)
    return f"{hours} h {minutes} min" if hours else f"{minutes} min"


@st.cache_resource(show_spinner="Loading the Act. The first start downloads the search model (about a minute)...")
def load_pipeline(index_name: str):
    """Load the index and LLM once per server process, shared by all visitors."""
    retriever = Retriever(index_name, settings=settings)
    llm = get_llm(settings, cache=False)  # answers vary; a cached bad one would stick for everyone
    return build_graph(retriever, llm, get_expand_llm(settings), checkpointer=chat_memory()), llm.model_name


def source_label(numbers: list[str]) -> str:
    return ", ".join(n if n.startswith("Schedule") else f"Section {n}" for n in numbers)


def debug_info(state: dict, steps: list[dict], calls: list[dict]) -> dict:
    """Everything the dev panel shows, as plain data (it is kept with the message)."""
    return {
        "total_ms": sum(s["ms"] for s in steps),
        "steps": steps,
        "llm_calls": calls,
        "standalone_question": state["standalone_question"],
        "errors": {k: state[k] for k in ("rewrite_error", "expand_error") if state.get(k)},
        "queries": state["queries"],
        "hits": [
            {"rank": h.rank, "score": round(h.score, 4), "sections": ", ".join(h.chunk.sections),
             "pages": ", ".join(map(str, h.chunk.pages)), "chunk_id": h.chunk.chunk_id,
             "neighbour of": h.neighbour_of or ""}
            for h in state["hits"]
        ],
        "history": state["history"],
    }


def ask(graph, question: str, mode: str, neighbours: bool, expand: bool, rerank: bool, index_name: str) -> dict:
    """Run the pipeline and keep only plain data, so the chat history can be re-drawn."""
    inputs = {"question": question, "mode": mode, "k": settings.answer_k, "neighbours": neighbours,
              "expand": expand, "rerank": rerank}
    # The graph's memory keeps this visitor's earlier turns under their thread id.
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    steps, last = [], time.perf_counter()
    with record_llm_calls() as calls:
        # "updates" yields once per finished node, so the time between yields is that node's time.
        for update in graph.stream(inputs, config, stream_mode="updates"):
            node, now = next(iter(update)), time.perf_counter()
            steps.append({"step": node, "ms": round((now - last) * 1000)})
            last = now
            for call in calls:
                call.setdefault("step", node)  # calls made since the previous node
    state = graph.get_state(config).values
    cited = set(state["citations"])
    sources = [
        {
            "label": source_label(h.chunk.sections),
            "titles": "; ".join(t for t in h.chunk.section_titles if t),
            "pages": h.chunk.pages,
            "text": h.chunk.text,
            "cited": bool(cited & set(h.chunk.sections)),
            "neighbour": h.neighbour_of is not None,
        }
        for h in state["hits"]
    ]
    return {
        "role": "assistant",
        "content": state["answer"],
        "refused": state["refused"],
        "unsupported": state["unsupported_citations"],
        "sources": sources,
        "mode": mode,
        "index": index_name,
        "reranked": rerank,
        "extra_queries": state.get("queries", [])[1:],  # [0] is the question itself
        # Shown when a follow-up was rewritten, so the reader sees what was actually searched.
        "standalone": state["standalone_question"] if state["standalone_question"] != question else None,
        "debug": debug_info(state, steps, calls) if settings.dev_mode else None,
    }


def _tokens(calls: list[dict], key: str) -> int:
    return sum((c["usage"] or {}).get(key, 0) for c in calls)


def show_debug(d: dict) -> None:
    """Dev mode only. Cache hits used no quota; their token counts are from the first call."""
    calls = d["llm_calls"]
    api = [c for c in calls if not c["cached"]]
    with st.expander("🛠 Dev metrics"):
        st.caption(
            f"{d['total_ms']:,} ms · {len(api)} API call(s), {len(calls) - len(api)} cache hit(s) · "
            f"API tokens: {_tokens(api, 'input'):,} in, {_tokens(api, 'output'):,} out "
            f"(of which {_tokens(api, 'thinking'):,} thinking)"
        )
        timing, retrieval, prompts, memory = st.tabs(["Time & tokens", "Retrieval", "Prompts", "Memory"])
        with timing:
            st.dataframe(d["steps"], hide_index=True)
            if calls:
                st.dataframe(
                    [{"step": c["step"], "model": c["model"], "cached": c["cached"], "ms": c["ms"],
                      **{k: (c["usage"] or {}).get(k) for k in ("input", "output", "thinking", "total")}}
                     for c in calls],
                    hide_index=True,
                )
        with retrieval:
            st.markdown(f"**Searched and answered as:** {d['standalone_question']}")
            for name, error in d["errors"].items():
                st.warning(f"{name}: {error}")
            st.markdown("**Queries:**\n" + "\n".join(f"{i}. {q}" for i, q in enumerate(d["queries"], 1)))
            st.dataframe(d["hits"], hide_index=True)
        with prompts:
            if not calls:
                st.caption("No LLM calls.")
            for c in calls:
                st.markdown(f"**{c['step']}** · `{c['model']}`" + (" · cached" if c["cached"] else ""))
                st.code(f"[system]\n{c['system']}\n\n[user]\n{c['user']}\n\n[reply]\n{c['reply']}",
                        language=None, wrap_lines=True)
        with memory:
            st.caption(f"Thread `{st.session_state.thread_id}` · {len(d['history'])} turn(s) stored, "
                       f"the last {settings.history_turns} used to rewrite follow-ups")
            st.json(d["history"], expanded=False)


def show_assistant(msg: dict) -> None:
    st.markdown(msg["content"])
    if msg.get("unsupported"):
        st.warning(
            f"The answer cites {', '.join(msg['unsupported'])}, which was not among the retrieved text. "
            "Treat that part with care."
        )
    show_sources(msg)
    if msg.get("debug"):
        show_debug(msg["debug"])


def show_sources(msg: dict) -> None:
    sources = msg.get("sources") or []
    if not sources:
        return
    n_cited = sum(s["cited"] for s in sources)
    with st.expander(f"Sources: {len(sources)} excerpts from the Act ({n_cited} cited)"):
        if msg.get("index"):  # older messages in a session may lack it
            reranked = " · reranked" if msg.get("reranked") else ""
            st.caption(f"Index: `{msg['index']}`{reranked}")
        if msg.get("standalone"):
            st.markdown(f"**Your question, read with the chat so far:** {msg['standalone']}")
        if msg.get("extra_queries"):
            st.markdown("**Also searched for:**\n" + "\n".join(f"- {q}" for q in msg["extra_queries"]))
        for s in sources:
            tags = " · cited" if s["cited"] else ""
            tags += " · added for context" if s["neighbour"] else ""
            pages = ", ".join(map(str, s["pages"]))
            st.markdown(f"**{s['label']}**: {s['titles']}  \nPage {pages}{tags}")
            st.code(s["text"], language=None, wrap_lines=True)


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("Settings")
    mode = st.radio(
        "How to search the Act",
        options=list(MODE_LABELS),
        format_func=MODE_LABELS.get,
        index=list(MODE_LABELS).index(settings.answer_mode),
        help="'Meaning' finds text with similar meaning. 'Keywords' matches exact words and numbers.",
    )
    neighbours = st.toggle(
        "Include surrounding text",
        value=settings.answer_neighbours,
        help="Also give the AI the text just before and after each match, from the same section. "
        "Helps with tables that are split across excerpts.",
    )
    expand = st.toggle(
        "Rewrite my question for search",
        value=settings.expand_queries,
        help="The AI also searches with versions of your question in the Act's own wording, "
        "e.g. '12 lakh' becomes 'Rs. 1200000' and 'TDS' becomes 'tax deducted at source'.",
    )
    rerank = st.toggle(
        "Rerank results",
        value=settings.rerank,
        help="A second, more careful model reads your question next to each search result and puts "
        "the best matches first. Slower (about 2 seconds) but more accurate: in our tests the right "
        "section came first for 23 of 23 questions, against 18 of 23 without it.",
    )
    st.divider()
    indexes = available_indexes()
    if len(indexes) > 1:
        index_name = st.selectbox(
            "How the Act is split for search",
            options=indexes,
            format_func=index_label,
            help="The Act is split into chunks before search. 'Fixed' cuts every 1,000 characters; "
            "'Structured' cuts where the Act does (sections, sub-sections, table rows). "
            "The first use of an index takes a few seconds to load.",
        )
        st.caption(f"Index: `{index_name}`")
    else:
        index_name = settings.index_name
        st.caption(f"Index: `{index_name}`")
    st.caption("Source: Income-tax Act, 2025, as amended by the Finance Act, 2026 (incometaxindia.gov.in).")

if "messages" not in st.session_state:
    st.session_state.messages = []
    # A random id per browser session: the graph's memory key. A page reload starts a new one.
    st.session_state.thread_id = uuid.uuid4().hex

if settings.dev_mode:
    with st.sidebar:
        st.divider()
        st.subheader("🛠 Dev mode")
        debug = [m["debug"] for m in st.session_state.messages if m.get("debug")]
        calls = [c for d in debug for c in d["llm_calls"]]
        api = [c for c in calls if not c["cached"]]
        st.caption(
            f"Thread `{st.session_state.thread_id}`  \n"
            f"This session: {len(debug)} answer(s), {len(api)} API call(s), {len(calls) - len(api)} cache hit(s)  \n"
            f"API tokens: {_tokens(api, 'input'):,} in, {_tokens(api, 'output'):,} out "
            f"({_tokens(api, 'thinking'):,} thinking)"
        )
        if st.button("New chat", help="Clear the messages and start a new memory thread."):
            st.session_state.messages = []
            st.session_state.thread_id = uuid.uuid4().hex
            st.rerun()

# ---------------------------------------------------------------- main
st.title("📘 Income-tax Act, 2025: Q&A")
st.info(
    "**Not tax advice.** Answers are generated by AI from the text of the Act and can be wrong "
    "or incomplete. Check the cited sections, or ask a tax professional."
)
st.caption("🔒 Don't type personal details. Your questions are sent to Google's Gemini API.")

try:
    graph, model_name = load_pipeline(index_name)
except Exception as e:  # missing index, bad key, unknown model: show it instead of a stack trace
    st.error(f"The app could not start: {e}")
    st.stop()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            show_assistant(msg)
        else:
            st.markdown(msg["content"])

limits, visitor = question_limits(), visitor_id()
window = f"{settings.question_window_hours:g} hours"
if settings.dev_mode:  # local testing: no limit
    blocked, status = None, f"Dev mode: no question limit · model: {model_name}"
else:
    mine, everyone = limits.left(visitor)
    blocked = None
    if everyone <= 0:
        blocked = ("The demo has reached its question limit for now, to stay within the free API quota. "
                   "Please try again later.")
    elif mine <= 0:
        blocked = (f"This demo allows {settings.max_questions_per_visitor} questions per {window}, "
                   f"to stay within the free API quota. You can ask again in "
                   f"{wait_text(limits.free_again_in(visitor))}.")
    status = f"{mine} question{'s' if mine != 1 else ''} left (per {window}) · model: {model_name}"

question = None
if not st.session_state.messages:
    st.write("Try one of these:")
    for i, example in enumerate(EXAMPLES):
        if st.button(example, key=f"example-{i}", disabled=bool(blocked)):
            question = example

typed = st.chat_input(
    "Question limit reached" if blocked else "Ask about the Income-tax Act, 2025",
    max_chars=500,
    disabled=bool(blocked),
)
question = typed or question

if blocked:
    st.caption(blocked)
elif st.session_state.messages:
    st.caption(status)

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Searching the Act and writing an answer..."):
                reply = ask(graph, question, mode, neighbours, expand, rerank, index_name)
        except QuotaExhausted:
            st.session_state.messages.pop()
            st.error("The free daily quota for the AI model is used up. Please try again tomorrow.")
            st.stop()
        except NotRetryable as e:
            st.session_state.messages.pop()
            st.error(f"The AI model rejected the request: {e}")
            st.stop()
        except Exception:
            # Rate limits are retried with backoff first; if we still fail, the API is busy.
            st.session_state.messages.pop()
            st.error("The AI service is busy right now. Please try again in a minute.")
            st.stop()
        show_assistant(reply)
    st.session_state.messages.append(reply)
    if not settings.dev_mode:
        used = limits.record(visitor)
        # For the owner (Streamlit Cloud: Manage app > Logs). A hash, not the IP: enough to see
        # whether visitors are told apart (if every visitor shows the same hash, the IP is the proxy's).
        print(f"[usage] {used}/{settings.max_questions_total} questions in the last {window} (all visitors) "
              f"· visitor {hashlib.sha256(visitor.encode()).hexdigest()[:8]}", flush=True)
    st.rerun()  # Redraw so the question counter and example buttons update.
