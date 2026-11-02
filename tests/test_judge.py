"""Judge parsing and answer-eval summary (no LLM calls)."""

import pytest
from judge import judge_prompt, parse_verdict, summarize_answers, uses_old_law


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
    assert "old_law" not in s  # only runs on trap questions report it


def test_uses_old_law_matches_only_the_repealed_figure():
    # Patterns from traps.jsonl t01 (old: 5% / 20%, current: 2%) and t04 (old: Rs 500 a day).
    assert uses_old_law("TCS is 5% up to Rs 10 lakh", [r"\b5%", r"\b20%"])
    assert not uses_old_law("TCS is 2% of the amount; 25% is not it either", [r"\b5%"])
    rs_500 = [r"(Rs\.?|₹|INR)\s?500(?![\d,])"]
    assert uses_old_law("a penalty of Rs. 500 for every day", rs_500)
    assert not uses_old_law("Rs. 500000 total income, Rs 5,00,000", rs_500)


def test_summarize_answers_counts_old_law_over_trap_rows_judged_or_not():
    rows = [
        {"type": "trap", "in_scope": True, "verdict": v("incorrect"), "old_law": True},
        {"type": "trap", "in_scope": True, "verdict": None, "old_law": False},  # judge failed
        {"type": "table", "in_scope": True, "verdict": v("correct")},  # not a trap
    ]
    assert summarize_answers(rows)["old_law"] == {"hits": 1, "n": 2, "rate": 0.5}
