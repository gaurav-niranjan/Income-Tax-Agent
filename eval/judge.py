"""LLM judge for the answer eval (Phase 7).

For each question the judge sees: the question, the human-checked reference answer, the
exact excerpts the app was given, and the app's answer. It grades:

- correctness: "correct" / "partial" / "incorrect" against the reference
- faithful:    every claim in the answer is supported by the excerpts (not the reference,
               not the judge's own knowledge). A refusal is faithful.
- refused:     the app declined / said it could not find the answer

The judge should be a different (ideally stronger) model than the one answering, so it
does not share the answerer's blind spots.
"""

import json
import re

CORRECTNESS = ("correct", "partial", "incorrect")

JUDGE_SYSTEM = """You grade answers from a question-answering app about India's Income-tax Act, 2025. \
The app must answer only from the excerpts of the Act it was given. Grade strictly and literally. \
Reply with one JSON object and nothing else."""

JUDGE_TEMPLATE = """Question: {question}

Scope: {scope}

Reference answer (checked against the Act by a human):
{reference}

Excerpts the app was given:
<<<
{context}
>>>

App's answer:
<<<
{answer}
>>>

Grade three things.

1. "correctness": compare the app's answer with the reference answer.
   - "correct": it gives the reference's key facts (amounts, rates, dates, and conditions that change the answer) and states nothing wrong. Extra correct detail is fine.
   - "partial": right in part, but it misses a key fact from the reference or gets a minor detail wrong.
   - "incorrect": a key fact is wrong, it answers a different question (for example it defines a narrower term than the one asked about), or it declines although the reference has an answer.
   For an out-of-scope question: "correct" if the app declines or says the Act does not cover it; "incorrect" if it gives a substantive answer.

2. "faithful": true if every factual claim in the app's answer is supported by the excerpts above. Judge only against the excerpts, not against the reference or your own knowledge. A refusal is faithful. False if any claim is not in the excerpts.

3. "refused": true if the app declined or said it could not find the answer.

Reply with JSON only, with these keys:
{{"correctness": "correct" | "partial" | "incorrect", "faithful": true | false, "refused": true | false, "unsupported_claims": [short strings; empty if faithful], "explanation": "one or two sentences"}}"""


def judge_prompt(question: str, reference: str, in_scope: bool, context: str, answer: str) -> str:
    scope = (
        "in scope: the Act answers this question"
        if in_scope
        else "out of scope: the Act does not cover this; the app should decline"
    )
    return JUDGE_TEMPLATE.format(
        question=question, scope=scope, reference=reference, context=context or "(none)", answer=answer
    )


def parse_verdict(text: str) -> dict:
    """Read the judge's JSON. Raises ValueError if it is missing or malformed."""
    match = re.search(r"\{.*\}", text, re.DOTALL)  # tolerate ```json fences or stray text
    if not match:
        raise ValueError(f"no JSON object in judge reply: {text[:200]!r}")
    v = json.loads(match.group(0))
    if v.get("correctness") not in CORRECTNESS:
        raise ValueError(f"bad correctness: {v.get('correctness')!r}")
    for key in ("faithful", "refused"):
        if not isinstance(v.get(key), bool):
            raise ValueError(f"{key} must be true/false, got {v.get(key)!r}")
    return {
        "correctness": v["correctness"],
        "faithful": v["faithful"],
        "refused": v["refused"],
        "unsupported_claims": [str(c) for c in v.get("unsupported_claims") or []],
        "explanation": str(v.get("explanation", "")),
    }


def _count(rows: list[dict], test) -> dict:
    hits = sum(1 for r in rows if test(r))
    return {"hits": hits, "n": len(rows), "rate": hits / len(rows) if rows else 0.0}


def summarize_answers(rows: list[dict]) -> dict:
    """rows: [{"type", "in_scope", "verdict": {...} or None}]. Unjudged rows are reported, not scored."""
    judged = [r for r in rows if r["verdict"]]
    in_scope = [r for r in judged if r["in_scope"]]
    out_scope = [r for r in judged if not r["in_scope"]]
    summary = {
        "unjudged": len(rows) - len(judged),
        "correct": _count(in_scope, lambda r: r["verdict"]["correctness"] == "correct"),
        "correct_or_partial": _count(in_scope, lambda r: r["verdict"]["correctness"] != "incorrect"),
        "faithful": _count(judged, lambda r: r["verdict"]["faithful"]),
        "refusal_out_of_scope": _count(out_scope, lambda r: r["verdict"]["refused"]),
        "false_refusal_in_scope": _count(in_scope, lambda r: r["verdict"]["refused"]),
        "by_type": {},
    }
    for t in dict.fromkeys(r["type"] for r in in_scope):
        group = [r for r in in_scope if r["type"] == t]
        summary["by_type"][t] = {
            c: _count(group, lambda r, c=c: r["verdict"]["correctness"] == c) for c in CORRECTNESS
        }
    return summary


def fmt(c: dict) -> str:
    return f"{c['rate']:.2f} ({c['hits']}/{c['n']})"

