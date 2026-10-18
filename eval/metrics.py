"""Retrieval metrics. No LLM needed.

For each question we find the rank of the first retrieved chunk that counts as a hit,
under three rules:

- section: the chunk lists one of the expected sections.
- strict:  one of the expected sections makes up at least 30% of the chunk's
           (non-space) characters. A chunk that only clips the edge of the right
           section is not a strict hit.
- phrase:  the chunk contains one of the expected phrases (case and spacing ignored).

From those ranks: hit@k = share of questions with a hit in the top k, and
MRR = mean of 1/rank (0 when there is no hit in the retrieved list).
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean

from income_tax_agent.ingest.chunkers.base import Chunk

STRICT_SHARE = 0.30
RULES = ("section", "strict", "phrase")
KS = (1, 3, 5)


@dataclass
class Question:
    id: str
    type: str
    question: str
    sections: list[str]
    phrases: list[str]
    reference: str
    extra: dict = field(default_factory=dict)

    @property
    def in_scope(self) -> bool:
        return self.type != "out_of_scope"


def load_questions(path: Path) -> list[Question]:
    with path.open(encoding="utf-8") as f:
        return [Question(**json.loads(line)) for line in f if line.strip()]


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def is_section_hit(chunk: Chunk, sections: list[str]) -> bool:
    return any(s in chunk.sections for s in sections)


def is_strict_hit(chunk: Chunk, sections: list[str], share: float = STRICT_SHARE) -> bool:
    chars = chunk.extra.get("section_chars", {})
    total = sum(chars.values())
    return total > 0 and any(chars.get(s, 0) / total >= share for s in sections)


def is_phrase_hit(chunk: Chunk, phrases: list[str]) -> bool:
    text = normalize(chunk.text)
    return any(normalize(p) in text for p in phrases)


def first_hit_ranks(ranked: list[tuple[int, Chunk]], q: Question) -> dict[str, int | None]:
    """Best rank of a hit under each rule, or None if no retrieved chunk hits.

    `ranked` is [(rank, chunk)]. Usually ranks are 1, 2, 3...; with neighbour expansion a
    neighbour carries the rank of the hit it was added for, so ranks repeat.
    """
    checks = {
        "section": lambda c: is_section_hit(c, q.sections),
        "strict": lambda c: is_strict_hit(c, q.sections),
        "phrase": lambda c: is_phrase_hit(c, q.phrases),
    }
    return {
        rule: min((rank for rank, c in ranked if check(c)), default=None)
        for rule, check in checks.items()
    }


def summarize(ranks: list[int | None]) -> dict[str, float]:
    """hit@1/3/5 (as a rate and a raw count) and MRR for one rule over a group of questions.

    Raw counts matter with ~22 questions: one question moves a rate by ~5 points.
    """
    out: dict[str, float] = {"n": len(ranks)}
    for k in KS:
        hits = sum(r is not None and r <= k for r in ranks)
        out[f"hits@{k}"] = hits
        out[f"hit@{k}"] = hits / len(ranks)
    out["mrr"] = mean(1 / r if r else 0.0 for r in ranks)
    return out


def format_metric(s: dict, metric: str) -> str:
    """"0.82 (18/22)" for hit@k, "0.71" for MRR."""
    if metric == "mrr":
        return f"{s['mrr']:.2f}"
    k = metric.removeprefix("hit@")
    return f"{s[metric]:.2f} ({s[f'hits@{k}']}/{s['n']})"


def summarize_by_type(rows: list[dict]) -> dict[str, dict]:
    """rows: [{"type": ..., "ranks": {rule: rank}}] for in-scope questions.

    Returns {group: {"n": n, rule: {metric: value}}}, with an "all" group first.
    """
    groups: dict[str, list[dict]] = {"all": rows}
    for row in rows:
        groups.setdefault(row["type"], []).append(row)
    return {
        name: {"n": len(g), **{rule: summarize([r["ranks"][rule] for r in g]) for rule in RULES}}
        for name, g in groups.items()
    }
