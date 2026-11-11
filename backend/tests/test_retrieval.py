"""Tests for Reciprocal Rank Fusion (RRF) and hybrid search logic."""

from app.retrieval.fusion import fuse_search_results, reciprocal_rank_fusion


def test_reciprocal_rank_fusion_single_list():
    ranked = [["doc_a", "doc_b", "doc_c"]]
    fused = reciprocal_rank_fusion(ranked, k=60)
    assert len(fused) == 3
    assert fused[0][0] == "doc_a"
    assert fused[1][0] == "doc_b"
    assert fused[2][0] == "doc_c"
    assert fused[0][1] == 1.0 / (60 + 1)


def test_reciprocal_rank_fusion_combines_ranks():
    list1 = ["doc_1", "doc_2", "doc_3"]
    list2 = ["doc_2", "doc_1", "doc_4"]
    fused = reciprocal_rank_fusion([list1, list2], k=60)

    # doc_1: 1/(61) + 1/(62)
    # doc_2: 1/(62) + 1/(61) -> exactly same score as doc_1
    top_ids = {fused[0][0], fused[1][0]}
    assert top_ids == {"doc_1", "doc_2"}

    # doc_3 appeared at rank 3 in list1: 1/63
    # doc_4 appeared at rank 3 in list2: 1/63
    lower_ids = {fused[2][0], fused[3][0]}
    assert lower_ids == {"doc_3", "doc_4"}


def test_fuse_search_results_with_metadata():
    vec_results = [
        {"id": 101, "text": "Apple Revenue", "meta": {"ticker": "AAPL"}},
        {"id": 102, "text": "Microsoft Revenue", "meta": {"ticker": "MSFT"}},
    ]
    fts_results = [
        {"id": 102, "text": "Microsoft Revenue", "meta": {"ticker": "MSFT"}},
        {"id": 103, "text": "Google Search", "meta": {"ticker": "GOOGL"}},
    ]

    fused = fuse_search_results(vec_results, fts_results, k=60)
    assert len(fused) == 3
    # 102 appeared in both lists, so it must rank first
    assert fused[0]["id"] == 102
    assert "rrf_score" in fused[0]
    assert fused[0]["meta"]["ticker"] == "MSFT"

