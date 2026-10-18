"""Reciprocal Rank Fusion (RRF): merge ranked lists using ranks only, not scores.

BM25 scores and vector distances are on different scales, so adding them is meaningless.
RRF gives each chunk sum(1 / (k + rank)) over the lists it appears in. k=60 is the value
from the original paper (Cormack et al., 2009); it stops the top rank from dominating.
"""

from collections import defaultdict


def reciprocal_rank_fusion(rankings: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    """rankings: lists of ids, best first. Returns (id, fused score), best first."""
    scores: dict[str, float] = defaultdict(float)
    for ranking in rankings:
        for rank, item in enumerate(ranking, start=1):
            scores[item] += 1.0 / (k + rank)
    # Sort by score; ties keep first-seen order (Python's sort is stable).
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
