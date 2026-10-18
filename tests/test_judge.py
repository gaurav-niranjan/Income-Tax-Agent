"""Judge parsing and answer-eval summary (no LLM calls)."""

import pytest
from judge import judge_prompt, parse_verdict, summarize_answers


def test_parse_verdict_accepts_fenced_json():
    reply = '```json\n{"correctness": "partial", "faithful": true, "refused": false, ' \
            '"unsupported_claims": [], "explanation": "Misses the 30% slab."}\n```'
    v = parse_verdict(reply)
    assert (v["correctness"], v["faithful"], v["refused"]) == ("partial", True, False)
    assert v["explanation"] == "Misses the 30% slab."


@pytest.mark.parametrize(
    "reply",
    [
        "I think it is correct.",
        '{"correctness": "mostly", "faithful": true, "refused": false}',
        '{"correctness": "correct", "faithful": "yes", "refused": false}',
    ],
)
def test_parse_verdict_rejects_bad_replies(reply):
    with pytest.raises(ValueError):
        parse_verdict(reply)


def test_judge_prompt_states_scope_and_includes_everything():
    p = judge_prompt("GST rate?", "Should refuse.", False, "[Excerpt 1 | Section 393]\ntext", "No idea.")
    assert "out of scope" in p and "GST rate?" in p and "Should refuse." in p
    assert "[Excerpt 1 | Section 393]" in p and "No idea." in p


def v(correctness, faithful=True, refused=False):
    return {"correctness": correctness, "faithful": faithful, "refused": refused}


def test_summarize_answers():
    rows = [
        {"type": "table", "in_scope": True, "verdict": v("correct")},
        {"type": "table", "in_scope": True, "verdict": v("partial", faithful=False)},
        {"type": "definition", "in_scope": True, "verdict": v("incorrect", refused=True)},
        {"type": "out_of_scope", "in_scope": False, "verdict": v("correct", refused=True)},
        {"type": "out_of_scope", "in_scope": False, "verdict": None},  # judge failed
    ]
    s = summarize_answers(rows)
    assert s["unjudged"] == 1
    assert (s["correct"]["hits"], s["correct"]["n"]) == (1, 3)
    assert s["correct_or_partial"]["hits"] == 2
    assert (s["faithful"]["hits"], s["faithful"]["n"]) == (3, 4)
    assert (s["refusal_out_of_scope"]["hits"], s["refusal_out_of_scope"]["n"]) == (1, 1)
    assert s["false_refusal_in_scope"]["hits"] == 1
    assert s["by_type"]["table"]["partial"]["hits"] == 1
