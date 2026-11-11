"""Reciprocal Rank Fusion (RRF) for combining ranked retrieval results."""

from collections import defaultdict
from typing import Any, Hashable


def reciprocal_rank_fusion[T: Hashable](
    ranked_lists: list[list[T]],
    k: int = 60,
) -> list[tuple[T, float]]:
    """Compute Reciprocal Rank Fusion scores across multiple ranked candidate lists.

    Formula for each document d:
        RRF_score(d) = sum(1.0 / (k + rank(d, lst)) for lst in ranked_lists if d in lst)
    where rank is 1-indexed.

    Args:
        ranked_lists: List of ranked candidate lists (ordered from best to worst).
        k: Smoothing constant (default 60, standard in literature).

    Returns:
        List of (item, rrf_score) tuples sorted in descending order of score.
    """
    scores: dict[T, float] = defaultdict(float)

    for ranking in ranked_lists:
        for rank, item in enumerate(ranking, start=1):
            scores[item] += 1.0 / (k + rank)

    sorted_items = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    return sorted_items


def fuse_search_results(
    vector_results: list[dict[str, Any]],
    fts_results: list[dict[str, Any]],
    k: int = 60,
    id_key: str = "id",
) -> list[dict[str, Any]]:
    """Merge vector and full-text search results using Reciprocal Rank Fusion.

    Retains the complete document metadata from whichever list contains it,
    attaching a computed `rrf_score` field.
    """
    items_by_id: dict[Any, dict[str, Any]] = {}

    vector_ids = []
    for item in vector_results:
        item_id = item[id_key]
        vector_ids.append(item_id)
        if item_id not in items_by_id:
            items_by_id[item_id] = dict(item)

    fts_ids = []
    for item in fts_results:
        item_id = item[id_key]
        fts_ids.append(item_id)
        if item_id not in items_by_id:
            items_by_id[item_id] = dict(item)

    fused_ranks = reciprocal_rank_fusion([vector_ids, fts_ids], k=k)

    result_docs = []
    for item_id, score in fused_ranks:
        doc = dict(items_by_id[item_id])
        doc["rrf_score"] = score
        result_docs.append(doc)

    return result_docs

