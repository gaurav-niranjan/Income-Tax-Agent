"""Run the Streamlit app headless with fake models and a tiny index (no keys, no downloads)."""

from pathlib import Path

import pytest
import streamlit as st
from helpers import make_page
from streamlit.testing.v1 import AppTest

from income_tax_agent.config import Settings, get_settings
from income_tax_agent.embeddings import FakeEmbeddings
from income_tax_agent.index import build_index
from income_tax_agent.ingest.chunkers.fixed import FixedSizeChunker

APP = str(Path(__file__).parents[1] / "app/streamlit_app.py")
BODY = """    Short title, extent and commencement.
    1. (1) This Act may be called the Income-tax Act, 2025.
    Deduction in respect of health insurance premia.
    2. (1) A deduction of Rs. 25,000 is allowed for health insurance premium."""


@pytest.fixture
def app(tmp_path, monkeypatch):
    out = build_index(FixedSizeChunker(200, 20), FakeEmbeddings(), Settings(index_dir=tmp_path, _env_file=None),
                      pages=[make_page(1, BODY)])
    monkeypatch.setenv("FAKE_MODELS", "1")
    monkeypatch.setenv("INDEX_DIR", str(tmp_path))
    monkeypatch.setenv("INDEX_NAME", out.name)
    monkeypatch.setenv("MAX_QUESTIONS_PER_VISITOR", "2")
    monkeypatch.setenv("DEV_MODE", "0")  # the local .env may turn it on, which lifts the cap
    get_settings.cache_clear()
    st.cache_resource.clear()
    yield AppTest.from_file(APP, default_timeout=30)
    get_settings.cache_clear()
    st.cache_resource.clear()


def test_app_shows_disclaimer_and_privacy_note(app):
    app.run()
    assert not app.exception
    assert "Not tax advice" in app.info[0].value
    assert any("Gemini API" in c.value for c in app.caption)


def test_question_gets_answer_with_sources(app):
    app.run()
    app.chat_input[0].set_value("health insurance premium deduction").run()
    assert not app.exception
    assistant = [m for m in app.chat_message if m.name == "assistant"]
    assert len(assistant) == 1
    assert "Fake answer" in assistant[0].markdown[0].value
    assert "Sources:" in assistant[0].expander[0].label


def test_no_index_picker_with_one_index(app):
    app.run()
    assert not app.selectbox
    assert any("Index:" in c.value for c in app.sidebar.caption)


def test_index_picker_switches_index(app, tmp_path):
    other = build_index(FixedSizeChunker(300, 30), FakeEmbeddings(), Settings(index_dir=tmp_path, _env_file=None),
                        pages=[make_page(1, BODY)])
    app.run()
    picker = app.sidebar.selectbox[0]
    assert picker.value == "fixed-200-20__fake"  # the configured default comes first
    # Visitors see plain labels from each manifest, not folder names.
    assert picker.options == ["Fixed 200-character chunks (default)", "Fixed 300-character chunks (experiment)"]
    picker.select(other.name).run()
    app.chat_input[0].set_value("health insurance premium deduction").run()
    assert not app.exception
    assistant = [m for m in app.chat_message if m.name == "assistant"]
    assert any(other.name in c.value for c in assistant[0].expander[0].caption)


def test_visitor_cap_survives_a_page_reload(app):
    app.run()
    for q in ("health insurance", "short title"):
        app.chat_input[0].set_value(q).run()
    assert app.chat_input[0].disabled
    assert any("questions per 24 hours" in c.value for c in app.caption)
    reloaded = AppTest.from_file(APP, default_timeout=30).run()  # a new browser session
    assert reloaded.chat_input[0].disabled
    assert all(b.disabled for b in reloaded.button)  # the example questions too


def test_cap_for_all_visitors(app, monkeypatch):
    monkeypatch.setenv("MAX_QUESTIONS_TOTAL", "1")
    app.run()
    app.chat_input[0].set_value("health insurance").run()
    assert app.chat_input[0].disabled
    assert any("Please try again later" in c.value for c in app.caption)


def test_no_cap_in_dev_mode(app, monkeypatch):
    monkeypatch.setenv("DEV_MODE", "1")
    app.run()
    for q in ("health insurance", "short title", "and the limit?"):
        app.chat_input[0].set_value(q).run()
    assert not app.exception
    assert not app.chat_input[0].disabled
    assert len([m for m in app.chat_message if m.name == "assistant"]) == 3


@pytest.mark.parametrize("on", [True, False])
def test_rerank_toggle(app, on):
    app.run()
    toggle = next(t for t in app.sidebar.toggle if t.label == "Rerank results")
    toggle.set_value(on).run()
    app.chat_input[0].set_value("health insurance premium deduction").run()
    assert not app.exception
    assistant = [m for m in app.chat_message if m.name == "assistant"]
    assert "Fake answer" in assistant[0].markdown[0].value
    assert any("reranked" in c.value for c in assistant[0].expander[0].caption) == on


def test_follow_up_uses_the_chat_so_far(app):
    app.run()
    app.chat_input[0].set_value("health insurance premium deduction").run()
    app.chat_input[0].set_value("and the limit?").run()
    assert not app.exception
    second = [m for m in app.chat_message if m.name == "assistant"][1]
    # FakeLLM's rewrite puts the previous question in front of the follow-up.
    assert any("health insurance premium deduction and the limit?" in md.value for md in second.expander[0].markdown)


@pytest.mark.parametrize("on", [True, False])
def test_dev_panel_only_in_dev_mode(app, monkeypatch, on):
    monkeypatch.setenv("DEV_MODE", "1" if on else "0")
    app.run()
    app.chat_input[0].set_value("health insurance premium deduction").run()
    assert not app.exception
    assistant = [m for m in app.chat_message if m.name == "assistant"][0]
    assert any("Dev metrics" in e.label for e in assistant.expander) == on
    assert any(s.value == "🛠 Dev mode" for s in app.sidebar.subheader) == on
    if on:  # one row per node that ran, timed from the graph's stream
        debug = app.session_state.messages[-1]["debug"]
        assert [s["step"] for s in debug["steps"]] == ["rewrite", "expand", "retrieve", "generate"]
        assert [c["step"] for c in debug["llm_calls"]] == ["expand", "generate"]


def test_question_with_query_rewrite_on(app):
    app.run()
    app.toggle[1].set_value(True).run()  # "Rewrite my question for search"
    app.chat_input[0].set_value("health insurance premium deduction").run()
    assert not app.exception
    assistant = [m for m in app.chat_message if m.name == "assistant"]
    assert "Fake answer" in assistant[0].markdown[0].value
