"""Chat with the Income-tax Act, 2025. Answers come only from the Act, with sources.

Run locally:  uv run streamlit run app/streamlit_app.py
On Streamlit Community Cloud, put GOOGLE_API_KEY and the model names in the app's Secrets.
With DEV_MODE=1 in .env, each answer also shows timings, tokens, prompts and chat memory.

Layout ("Workbench"): left, a table of contents of this chat; middle, every turn in order with
the input at the end; right, the search settings and the sources of ONE answer, the focused one.
"""

import hashlib
import json
import math
import os
import time
import uuid
from html import escape

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

st.set_page_config(page_title="Income Tax Act Q&A", page_icon="📘", layout="wide")


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
from income_tax_agent.prompts import CITATION_RE, parse_citations  # noqa: E402
from income_tax_agent.retrieval.retriever import Retriever  # noqa: E402

MODE_LABELS = {
    "dense": "Meaning",
    "hybrid": "+ Keywords",
    "bm25": "Keywords",
}
EXAMPLES = [
    "What are the income tax rates under the new regime?",
    "How many days must I stay in India to count as a resident?",
    "What is the GST rate on restaurant food?",
]
DISCLAIMER = (
    "AI-written from the Act. It can be wrong or incomplete. Check the sources, or ask a tax "
    "professional. Don't type personal details: questions go to Google's Gemini API."
)
# Colours and fonts are in .streamlit/config.toml. This is only what the theme can't set.
# Selectors use our own classes and the st-key-<key> class of keyed containers, not
# Streamlit's internal names, which change between versions.
CSS = """<style>
@import url("https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@500;600&family=Spectral&display=swap");
:root { --panel: #fbfbf9; --soft: #646b70; --hair: #d9dcd6; --ochre: #b77b12; --sel: #f3ead6;
  --ok: #2e6b4f; --warn: #a8680a; --f-label: "IBM Plex Sans Condensed", sans-serif;
  --f-mono: "IBM Plex Mono", monospace; --f-act: "Spectral", Georgia, serif; }
[data-testid="stMainBlockContainer"] { padding-left: 1rem; padding-right: 1rem; }
/* Each panel fills the window and scrolls on its own: size the wrapper that holds the fixed height. */
.st-key-left, .st-key-mid, .st-key-right { background: var(--panel); }
div:has(> .st-key-left), div:has(> .st-key-right) { --h: calc(100vh - 158px); }
div:has(> .st-key-flow) { --h: calc(100vh - 292px); }
div:has(> .st-key-left), div:has(> .st-key-right), div:has(> .st-key-flow) { height: var(--h); flex-basis: var(--h); }
@media (max-width: 640px) { div:has(> .st-key-left), div:has(> .st-key-right), div:has(> .st-key-flow) { --h: auto; } }
.top { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 6px 16px; }
.top h1 { font: 600 28px/1.1 var(--f-label); letter-spacing: .01em; text-transform: uppercase; margin: 0; padding: 0;
  color: #16191c; }
.top .yr { color: var(--ochre); }
.top p { margin: 4px 0 0; font-size: 13px; color: var(--soft); }
.top small { font: 12px var(--f-mono); color: var(--warn); border: 1px solid currentColor; border-radius: 99px; padding: 3px 10px; }
.lab { font: 600 11px var(--f-label); letter-spacing: .08em; text-transform: uppercase; color: var(--soft);
  display: flex; justify-content: space-between; gap: 6px; }
.toc a { display: grid; gap: 2px; padding: 8px 10px; border-left: 3px solid transparent; color: inherit;
  text-decoration: none; font-size: 13px; line-height: 1.35; }
.toc a:hover { background: #f1f1ec; }
.toc a.focus { background: var(--sel); border-left-color: var(--ochre); }
.toc small, .n { font: 11px var(--f-mono); color: var(--soft); }
.toc small.no { color: var(--warn); }
.st-key-examples button { border-style: dashed; color: var(--soft); text-align: left; }
.st-key-examples button > * { justify-content: flex-start; }
.bar { display: flex; gap: 3px; margin: 6px 0; }
.bar i { flex: 1; height: 6px; border-radius: 1px; background: #16191c; }
.bar i.u { background: var(--hair); }
[class*="st-key-turn"] { border-bottom: 1px solid var(--hair); padding: 10px 0 18px; }
[class*="st-key-turn-focus"] h3 { box-shadow: inset 3px 0 0 var(--ochre); padding-left: 10px; }
:not(pre) > code { font-size: .8em; border: 1px solid var(--hair); border-bottom-width: 2px; border-radius: 4px;
  padding: 0 5px; white-space: nowrap; }
[class*="st-key-foot"] p { font: 12px var(--f-mono); }
[class*="st-key-foot"] button { min-height: 0; padding: 2px 10px; }
.card { padding: 10px 0; border-bottom: 1px solid var(--hair); display: grid; gap: 4px; }
.card .h { display: flex; justify-content: space-between; gap: 8px; font: 500 12px var(--f-mono); }
.card .h span + span, .card .ttl { color: var(--soft); font-weight: 400; }
.card .ttl { font-size: 12.5px; }
.card .tx { font: 14px/1.6 var(--f-act); color: #2b3035; white-space: pre-line; }
.card .tag { font: 10.5px var(--f-mono); color: var(--ok); }
.card .tag.ctx { color: var(--soft); }
.st-key-status { position: fixed; left: 0; right: 0; bottom: 0; z-index: 100; padding: 5px 16px;
  background: #e2e5e0; border-top: 1px solid var(--hair); }
.st-key-status p { font: 11.5px var(--f-mono); }
.st-key-status strong { color: #16191c; font-weight: 500; }
</style>"""

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


def label(left: str, right: str = "") -> None:
    """A small upper-case panel label, e.g. "THIS CHAT ... 3"."""
    st.markdown(f'<div class="lab"><span>{left}</span><span>{right}</span></div>', unsafe_allow_html=True)


def cite_tags(answer: str) -> str:
    """Show "[Section 6(2)(a)]" as a small key "§6(2)(a)" (inline code, styled by the CSS).
    Display only: the stored answer keeps the brackets."""
    return CITATION_RE.sub(
        lambda m: f"`{m.group()[1:-1].replace('Sections ', '§§').replace('Section ', '§')}`", answer
    )


def toc_meta(msg: dict) -> tuple[str, str]:
    """The small line under a question in the table of contents: what it cites, e.g. "s. 6"."""
    cited = parse_citations(msg["content"])
    if msg.get("refused"):
        text, css = "not found in the Act", "no"
    elif cited:
        text, css = ", ".join(c.replace("Schedule", "Sch.") if c.startswith("Schedule") else f"s. {c}"
                              for c in cited), ""
    else:
        text, css = "no citations", ""
    return text, css


def pick_sources() -> None:
    st.session_state.focus = st.session_state.source_pick


def show_turn(n: int, question: str, msg: dict, focused: bool) -> None:
    """One question and its answer in the middle panel."""
    with st.container(key=f"turn-focus-{n}" if focused else f"turn-{n}"):
        st.markdown(f'<span class="n">{n}</span>', unsafe_allow_html=True)
        st.subheader(question, anchor=f"q{n}")
        if msg.get("standalone"):
            st.caption(f"Searched as: *{msg['standalone']}*")
        st.markdown(cite_tags(msg["content"]))
        sources = msg.get("sources") or []
        with st.container(key=f"foot-{n}", horizontal=True, vertical_alignment="center", gap="medium"):
            if msg.get("unsupported"):
                st.caption(f":orange[⚠ cites {source_label(msg['unsupported'])}, which was not among the "
                           "retrieved text. Treat that part with care.]", width="content")
            elif parse_citations(msg["content"]):
                st.caption(":green[✓] citations found in the sources", width="content")
            if sources:
                st.caption(f"{len(sources)} excerpts · {sum(s['cited'] for s in sources)} cited", width="content")
        if msg.get("debug"):
            show_debug(msg["debug"])


def show_sources(focused: int, answers: list[int], messages: list[dict]) -> None:
    """The focused answer's excerpts in the right panel, split into cited and not cited.
    A picker switches to an earlier answer."""
    st.divider()
    if len(answers) > 1:
        label("Sources")
        st.session_state.source_pick = focused  # follow new answers
        st.selectbox("Show the sources of", answers, key="source_pick", on_change=pick_sources,
                     format_func=lambda i: f"{answers.index(i) + 1}. {messages[i - 1]['content']}")
    else:
        label("Sources", "question 1")
    msg = messages[focused]
    sources = msg.get("sources") or []
    if not sources:
        st.caption("Nothing was retrieved for this answer.")
        return
    if msg.get("extra_queries"):
        st.caption("Also searched for: " + " · ".join(f"*{q}*" for q in msg["extra_queries"]))
    cited = [s for s in sources if s["cited"]]
    other = [s for s in sources if not s["cited"]]
    for tab, group in zip(st.tabs([f"Cited · {len(cited)}", f"Also read · {len(other)}"]), (cited, other)):
        with tab:
            if not group:
                st.caption("None.")
            for s in group:
                tags = " · ".join(t for t, on in (("cited", s["cited"]), ("added for context", s["neighbour"])) if on)
                st.html(
                    f'<div class="card"><div class="h"><span>{escape(s["label"])}</span>'
                    f'<span>p. {", ".join(map(str, s["pages"]))}</span></div>'
                    f'<div class="ttl">{escape(s["titles"])}</div><div class="tx">{escape(s["text"])}</div>'
                    + (f'<span class="tag{"" if s["cited"] else " ctx"}">{tags}</span>' if tags else "")
                    + "</div>"
                )


# ---------------------------------------------------------------- page
st.html(CSS)
st.markdown('<div class="top"><div><h1>Income-tax Act <span class="yr">2025</span> · Q&amp;A</h1>'
            "<p>Ask in plain English. Answers come only from the Act, as amended by the Finance Act, 2026, "
            "and cite the sections they use.</p></div><small>Not tax advice</small></div>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
    # A random id per browser session: the graph's memory key. A page reload starts a new one.
    st.session_state.thread_id = uuid.uuid4().hex

messages = st.session_state.messages
answers = [i for i, m in enumerate(messages) if m["role"] == "assistant"]
# The answer whose sources the right panel shows: the one picked there, else the latest.
# This is display only. A new question always follows on from the whole chat (the graph's memory).
focused = st.session_state.get("focus")
focused = focused if focused in answers else (answers[-1] if answers else None)

left_col, mid_col, right_col = st.columns([1, 3, 1.5])
left = left_col.container(key="left", border=True, height=600)  # real height: the CSS
mid = mid_col.container(key="mid", border=True)
right = right_col.container(key="right", border=True, height=600)

# ---------------------------------------------------------------- right: search setup
with right:
    label("Search setup", "next question")
    mode = st.segmented_control(
        "How to search the Act",
        options=list(MODE_LABELS),
        format_func=MODE_LABELS.get,
        default=settings.answer_mode,
        required=True,
        width="stretch",
        help="'Meaning' finds text with similar meaning. 'Keywords' matches exact words and numbers. "
        "'+ Keywords' uses both.",
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
    else:
        index_name = settings.index_name
    st.caption(f"Index: `{index_name}`  \n"
               "Source: Income-tax Act, 2025, as amended by the Finance Act, 2026 (incometaxindia.gov.in).")

try:
    graph, model_name = load_pipeline(index_name)
except Exception as e:  # missing index, bad key, unknown model: show it instead of a stack trace
    st.error(f"The app could not start: {e}")
    st.stop()

limits, visitor = question_limits(), visitor_id()
window = f"{settings.question_window_hours:g} hours"
if settings.dev_mode:  # local testing: no limit
    blocked, mine = None, None
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

# ---------------------------------------------------------------- left: table of contents
question = None
with left:
    label("This chat", str(len(answers)))
    if answers:
        # Plain anchor links: clicking one only scrolls. It never changes what a new question follows on from.
        items = ""
        for n, i in enumerate(answers, 1):
            meta, css = toc_meta(messages[i])
            items += (f'<a href="#q{n}" class="{"focus" if i == focused else ""}">'
                      f'<span>{escape(messages[i - 1]["content"])}</span><small class="{css}">{meta}</small></a>')
        st.markdown(f'<div class="toc">{items}</div>', unsafe_allow_html=True)
    else:
        st.caption("Your questions will be listed here.")
        label("Try")
        with st.container(key="examples"):
            for i, example in enumerate(EXAMPLES):
                if st.button(example, key=f"example-{i}", disabled=bool(blocked), width="stretch"):
                    question = example
    st.divider()
    if mine is None:
        st.caption(f"Dev mode: no question limit · model {model_name}")
    else:
        total = settings.max_questions_per_visitor
        bar = "".join("<i></i>" if k < mine else '<i class="u"></i>' for k in range(total))
        label("Questions left")
        st.markdown(f'<div class="bar">{bar}</div>', unsafe_allow_html=True)
        st.caption(f"{mine} of {total} per {window} · model {model_name}")

# ---------------------------------------------------------------- middle: every turn, then the input
with mid:
    flow = st.container(key="flow", height=600, border=False, autoscroll=True)  # real height: the CSS
    with flow:
        for n, i in enumerate(answers, 1):
            show_turn(n, messages[i - 1]["content"], messages[i], i == focused)
        if not answers:
            st.caption("Ask a question about the Income-tax Act, 2025. The answer cites the sections it uses.")
    st.caption(DISCLAIMER)
    typed = st.chat_input(
        "Question limit reached" if blocked else "Ask a follow-up, or a new question" if answers
        else "Ask about the Income-tax Act, 2025",
        max_chars=500,
        disabled=bool(blocked),
    )
    if blocked:
        st.caption(blocked)
question = typed or question

# ---------------------------------------------------------------- right: sources of the focused answer
if focused is not None:
    msg = messages[focused]
    with right:
        show_sources(focused, answers, messages)
    with st.container(key="status", horizontal=True):
        st.caption(
            f"answer **{answers.index(focused) + 1}** · index **{msg.get('index', '?')}** · "
            f"search **{MODE_LABELS.get(msg.get('mode'), '?')}** · "
            f"rerank **{'on' if msg.get('reranked') else 'off'}** · model **{model_name}**"
        )

if settings.dev_mode:
    with right:
        st.divider()
        label("🛠 Dev mode")
        debug = [m["debug"] for m in messages if m.get("debug")]
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
            st.session_state.pop("focus", None)
            st.rerun()

if question:
    with flow, st.container(key="turn-new"):
        st.markdown(f'<span class="n">{len(answers) + 1}</span>', unsafe_allow_html=True)
        st.subheader(question, anchor=False)
        messages.append({"role": "user", "content": question})
        try:
            with st.spinner("Searching the Act and writing an answer..."):
                reply = ask(graph, question, mode, neighbours, expand, rerank, index_name)
        except QuotaExhausted:
            messages.pop()
            st.error("The free daily quota for the AI model is used up. Please try again tomorrow.")
            st.stop()
        except NotRetryable as e:
            messages.pop()
            st.error(f"The AI model rejected the request: {e}")
            st.stop()
        except Exception:
            # Rate limits are retried with backoff first; if we still fail, the API is busy.
            messages.pop()
            st.error("The AI service is busy right now. Please try again in a minute.")
            st.stop()
    messages.append(reply)
    st.session_state.focus = len(messages) - 1  # a new answer becomes the focused one
    if not settings.dev_mode:
        used = limits.record(visitor)
        # For the owner (Streamlit Cloud: Manage app > Logs). A hash, not the IP: enough to see
        # whether visitors are told apart (if every visitor shows the same hash, the IP is the proxy's).
        print(f"[usage] {used}/{settings.max_questions_total} questions in the last {window} (all visitors) "
              f"· visitor {hashlib.sha256(visitor.encode()).hexdigest()[:8]}", flush=True)
    st.rerun()  # Redraw: the new turn, its sources on the right, the question counter.
