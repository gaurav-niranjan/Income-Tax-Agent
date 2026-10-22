"""Chat with the Income-tax Act, 2025. Answers come only from the Act, with sources.

Run locally:  uv run streamlit run app/streamlit_app.py
On Streamlit Community Cloud, put GOOGLE_API_KEY and the model names in the app's Secrets.
"""

import json
import os

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
from income_tax_agent.graph.build import build_graph  # noqa: E402
from income_tax_agent.llm import NotRetryable, QuotaExhausted, get_expand_llm, get_llm  # noqa: E402
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


@st.cache_resource(show_spinner="Loading the Act. The first start downloads the search model (about a minute)...")
def load_pipeline(index_name: str):
    """Load the index and LLM once per server process, shared by all visitors."""
    retriever = Retriever(index_name, settings=settings)
    llm = get_llm(settings)
    return build_graph(retriever, llm, get_expand_llm(settings)), llm.model_name


def source_label(numbers: list[str]) -> str:
    return ", ".join(n if n.startswith("Schedule") else f"Section {n}" for n in numbers)


def ask(graph, question: str, mode: str, neighbours: bool, expand: bool, index_name: str) -> dict:
    """Run the pipeline and keep only plain data, so the chat history can be re-drawn."""
    state = graph.invoke(
        {"question": question, "mode": mode, "k": settings.answer_k, "neighbours": neighbours, "expand": expand}
    )
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
        "extra_queries": state.get("queries", [])[1:],  # [0] is the question itself
    }


def show_assistant(msg: dict) -> None:
    st.markdown(msg["content"])
    if msg.get("unsupported"):
        st.warning(
            f"The answer cites {', '.join(msg['unsupported'])}, which was not among the retrieved text. "
            "Treat that part with care."
        )
    sources = msg.get("sources") or []
    if not sources:
        return
    n_cited = sum(s["cited"] for s in sources)
    with st.expander(f"Sources: {len(sources)} excerpts from the Act ({n_cited} cited)"):
        if msg.get("index"):  # older messages in a session may lack it
            st.caption(f"Index: `{msg['index']}`")
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

# ---------------------------------------------------------------- main
st.title("📘 Income-tax Act, 2025: Q&A")
st.info(
    "**Not tax advice.** Answers are generated by AI from the text of the Act and can be wrong "
    "or incomplete. Check the cited sections, or ask a tax professional."
)
st.caption("🔒 Don't type personal details. Your questions are sent to Google's Gemini API.")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.asked = 0

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

left = settings.max_questions_per_session - st.session_state.asked
question = None
if not st.session_state.messages:
    st.write("Try one of these:")
    for i, example in enumerate(EXAMPLES):
        if st.button(example, key=f"example-{i}", disabled=left <= 0):
            question = example

typed = st.chat_input(
    "Ask about the Income-tax Act, 2025" if left > 0 else "Question limit reached for this session",
    max_chars=500,
    disabled=left <= 0,
)
question = typed or question

if left <= 0:
    st.caption(
        f"This demo allows {settings.max_questions_per_session} questions per session, "
        "to stay within the free API quota."
    )
elif st.session_state.messages:
    st.caption(f"{left} question{'s' if left != 1 else ''} left in this session · model: {model_name}")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Searching the Act and writing an answer..."):
                reply = ask(graph, question, mode, neighbours, expand, index_name)
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
    st.session_state.asked += 1
    st.rerun()  # Redraw so the question counter and example buttons update.
