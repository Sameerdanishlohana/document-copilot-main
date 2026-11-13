"""Integration tests for hybrid retrieval against the ingested 10-K corpus.

Runs actual hybrid retrieval queries (pgvector + full-text search + RRF)
against sample analyst questions from client-brief.md.
"""

import pytest

from app.retrieval.retriever import DocumentRetriever


@pytest.mark.integration
def test_retriever_apple_revenue_mix():
    retriever = DocumentRetriever()
    results = retriever.search(
        query="Across Apple 10-Ks, revenue mix between iPhone, Services, Mac, iPad, and Wearables",
        ticker="AAPL",
        fiscal_year=2024,
        top_k=5,
    )
    assert len(results) > 0
    top = results[0]
    assert "rrf_score" in top
    assert top["metadata"]["ticker"] == "AAPL"
    assert "neighbors" in top
    # The retrieved text should mention at least one key product or revenue category
    combined_text = " ".join([r["text"] for r in results]).lower()
    assert any(term in combined_text for term in ["iphone", "services", "sales", "revenue"])


@pytest.mark.integration
def test_retriever_nvidia_datacenter_demand():
    retriever = DocumentRetriever()
    results = retriever.search(
        query="NVIDIA demand drivers, customer concentration, and supply constraints for Data Center",
        ticker="NVDA",
        fiscal_year=2024,
        top_k=5,
    )
    assert len(results) > 0
    combined_text = " ".join([r["text"] for r in results]).lower()
    assert any(term in combined_text for term in ["data center", "gpu", "compute", "revenue"])


@pytest.mark.integration
def test_retriever_amazon_aws_profitability():
    retriever = DocumentRetriever()
    results = retriever.search(
        query="Amazon AWS operating income and margin compared to North America and International segments",
        ticker="AMZN",
        fiscal_year=2024,
        top_k=5,
    )
    assert len(results) > 0
    combined_text = " ".join([r["text"] for r in results]).lower()
    assert any(term in combined_text for term in ["aws", "operating income", "net sales", "segment"])

