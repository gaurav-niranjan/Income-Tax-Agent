"""Merge ranked lists using ranks only, not scores.

BM25 scores and vector distances are on different scales, so adding them is meaningless.

Reciprocal Rank Fusion (RRF) gives each chunk sum(1 / (k + rank)) over the lists it appears
in. The paper's k=60 (Cormack et al., 2009) makes rank 1 worth barely more than rank 10, so
a chunk that is mediocre in every list beats one that is first in a single list. We use a
small k (see config.rrf_k).

Best-rank fusion ranks each chunk by its best rank in any list, and uses the RRF sum only to
break ties. Every list's #1 is in the top len(rankings). Used to merge the lists of the
query-expansion queries, where one rewrite often finds the right section on its own.
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


def best_rank_fusion(rankings: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    """Like reciprocal_rank_fusion, but the score is 1 / (k + best rank in any list).

    Ties (e.g. two lists' #1s) are broken by the RRF sum, so agreement still counts.
    """
    total = dict(reciprocal_rank_fusion(rankings, k))
    best: dict[str, float] = {}
    for ranking in rankings:
        for rank, item in enumerate(ranking, start=1):
            best[item] = max(best.get(item, 0.0), 1.0 / (k + rank))
    order = sorted(best, key=lambda item: (best[item], total[item]), reverse=True)
    return [(item, best[item]) for item in order]


FUSIONS = {"rrf": reciprocal_rank_fusion, "max": best_rank_fusion}
