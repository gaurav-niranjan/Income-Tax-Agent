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


def panel(app, key: str):
    """A keyed part of the page: "left", "flow" (the turns), "right" or "status"."""
    return app.get_by_key(key)


def status(app) -> str:
    return panel(app, "status").caption[0].value


def test_app_shows_disclaimer_and_privacy_note(app):
    app.run()
    assert not app.exception
    assert any("Not tax advice" in m.value for m in app.markdown)
    assert any("Gemini API" in c.value for c in app.caption)


def test_question_gets_answer_with_sources(app):
    app.run()
    app.chat_input[0].set_value("health insurance premium deduction").run()
    assert not app.exception
    flow = panel(app, "flow")
    assert [s.value for s in flow.subheader] == ["health insurance premium deduction"]
    assert any("Fake answer" in m.value for m in flow.markdown)
    assert [b.label for b in flow.button] == ["Sources"]
    assert [t.label for t in panel(app, "right").tabs] == ["Cited · 1", "Also read · 1"]
    assert any('href="#q1"' in m.value for m in panel(app, "left").markdown)  # table of contents


def test_citations_show_as_tags_but_are_stored_unchanged(app):
    app.run()
    app.chat_input[0].set_value("health insurance premium deduction").run()
    assert any("`§1`" in m.value for m in panel(app, "flow").markdown)
    assert "[Section 1]" in app.session_state.messages[-1]["content"]


def test_sources_button_focuses_an_answer_but_not_the_follow_up(app, monkeypatch):
    monkeypatch.setenv("DEV_MODE", "1")  # no question cap
    app.run()
    app.chat_input[0].set_value("health insurance premium deduction").run()
    app.chat_input[0].set_value("short title").run()
    assert status(app).startswith("answer **2**")  # the latest answer is focused
    panel(app, "flow").button[0].click().run()  # "Sources" under answer 1
    assert status(app).startswith("answer **1**")
    assert panel(app, "right").get_by_key("source_pick").value == 1  # the picker follows (message index)
    # A follow-up still builds on the latest turn, not on the focused one.
    app.chat_input[0].set_value("and the limit?").run()
    assert any("short title and the limit?" in c.value for c in panel(app, "flow").caption)
    assert status(app).startswith("answer **3**")  # a new answer becomes the focused one


def test_source_picker_shows_an_earlier_answer(app, monkeypatch):
    monkeypatch.setenv("DEV_MODE", "1")  # no question cap
    app.run()
    app.chat_input[0].set_value("health insurance premium deduction").run()
    assert not panel(app, "right").selectbox  # one answer: nothing to pick
    app.chat_input[0].set_value("short title").run()
    picker = panel(app, "right").get_by_key("source_pick")
    assert picker.options == ["1. health insurance premium deduction", "2. short title"]
    picker.set_value(1).run()  # values are message indexes: answer 1 is messages[1]
    assert status(app).startswith("answer **1**")
    assert panel(app, "flow").button[0].proto.type == "primary"  # its "Sources" button shows the focus


def test_no_index_picker_with_one_index(app):
    app.run()
    assert not app.selectbox
    assert any("Index:" in c.value for c in panel(app, "right").caption)


def test_index_picker_switches_index(app, tmp_path):
    other = build_index(FixedSizeChunker(300, 30), FakeEmbeddings(), Settings(index_dir=tmp_path, _env_file=None),
                        pages=[make_page(1, BODY)])
    app.run()
    picker = panel(app, "right").selectbox[0]
    assert picker.value == "fixed-200-20__fake"  # the configured default comes first
    # Visitors see plain labels from each manifest, not folder names.
    assert picker.options == ["Fixed 200-character chunks (default)", "Fixed 300-character chunks (experiment)"]
    picker.select(other.name).run()
    app.chat_input[0].set_value("health insurance premium deduction").run()
    assert not app.exception
    assert f"index **{other.name}**" in status(app)


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
    assert len(panel(app, "flow").subheader) == 3


@pytest.mark.parametrize("on", [True, False])
def test_rerank_toggle(app, on):
    app.run()
    toggle = next(t for t in panel(app, "right").toggle if t.label == "Rerank results")
    toggle.set_value(on).run()
    app.chat_input[0].set_value("health insurance premium deduction").run()
    assert not app.exception
    assert any("Fake answer" in m.value for m in panel(app, "flow").markdown)
    assert f"rerank **{'on' if on else 'off'}**" in status(app)


def test_follow_up_uses_the_chat_so_far(app):
    app.run()
    app.chat_input[0].set_value("health insurance premium deduction").run()
    app.chat_input[0].set_value("and the limit?").run()
    assert not app.exception
    # FakeLLM's rewrite puts the previous question in front of the follow-up.
    assert any(c.value == "Searched as: *health insurance premium deduction and the limit?*"
               for c in panel(app, "flow").caption)


@pytest.mark.parametrize("on", [True, False])
def test_dev_panel_only_in_dev_mode(app, monkeypatch, on):
    monkeypatch.setenv("DEV_MODE", "1" if on else "0")
    app.run()
    app.chat_input[0].set_value("health insurance premium deduction").run()
    assert not app.exception
    assert any("Dev metrics" in e.label for e in panel(app, "flow").expander) == on
    assert any("Dev mode" in m.value for m in panel(app, "right").markdown) == on
    if on:  # one row per node that ran, timed from the graph's stream
        debug = app.session_state.messages[-1]["debug"]
        assert [s["step"] for s in debug["steps"]] == ["rewrite", "expand", "retrieve", "generate"]
        assert [c["step"] for c in debug["llm_calls"]] == ["expand", "generate"]


def test_question_with_query_rewrite_on(app):
    app.run()
    app.toggle[1].set_value(True).run()  # "Rewrite my question for search"
    app.chat_input[0].set_value("health insurance premium deduction").run()
    assert not app.exception
    assert any("Fake answer" in m.value for m in panel(app, "flow").markdown)
