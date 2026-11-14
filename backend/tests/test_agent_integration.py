"""Integration tests for Phase 6 LLM answer generation and citation grounding."""

import json
from unittest.mock import MagicMock
import anyio
import pytest

from app.chat.orchestrator import run_turn


@pytest.mark.integration
@pytest.mark.anyio
async def test_orchestrator_grounded_answer_with_citations():
    mock_supabase = MagicMock()
    mock_supabase.table().insert().execute.return_value.data = [{"id": 101}]
    mock_supabase.table().update().eq().execute.return_value.data = [{}]

    mock_retriever = MagicMock()
    mock_retriever.search.return_value = [
        {
            "id": 55,
            "metadata": {
                "ticker": "AAPL",
                "company": "Apple Inc.",
                "filing_type": "10-K",
                "filing_date": "2024-11-01",
                "fiscal_year": 2024,
            },
            "page": "32",
            "section": "Item 7",
            "text": "iPhone net sales were $201,183 million in fiscal year 2024 compared to $200,583 million in fiscal year 2023.",
        }
    ]

    events = []
    async for event in run_turn(
        user_query="What were iPhone sales in 2024 for Apple?",
        thread_id=1,
        user_id="analyst-1",
        supabase_client=mock_supabase,
        retriever=mock_retriever,
    ):
        events.append(event)

    # Should emit text deltas (0:), citations data (2:), and finish (d:)
    assert any(e.startswith("0:") for e in events)
    assert any(e.startswith("2:") for e in events)
    assert any(e.startswith("d:") for e in events)


@pytest.mark.integration
@pytest.mark.anyio
async def test_orchestrator_refuses_when_no_evidence():
    mock_supabase = MagicMock()
    mock_supabase.table().insert().execute.return_value.data = [{"id": 102}]
    mock_supabase.table().update().eq().execute.return_value.data = [{}]

    mock_retriever = MagicMock()
    # Unrelated passage
    mock_retriever.search.return_value = [
        {
            "id": 88,
            "metadata": {
                "ticker": "MSFT",
                "company": "Microsoft Corporation",
                "filing_type": "10-K",
                "filing_date": "2024-07-30",
                "fiscal_year": 2024,
            },
            "page": "15",
            "section": "Item 1",
            "text": "We operate globally in various segments.",
        }
    ]

    events = []
    async for event in run_turn(
        user_query="What was Tesla's Cybertruck margin in 2024?",
        thread_id=1,
        user_id="analyst-1",
        supabase_client=mock_supabase,
        retriever=mock_retriever,
    ):
        events.append(event)

    text_parts = [json.loads(e.strip()[2:]) for e in events if e.startswith("0:")]
    full_text = "".join(text_parts).lower()

    # The model must declare lack of evidence
    assert any(phrase in full_text for phrase in ["not contain enough evidence", "insufficient", "no evidence", "not disclose", "does not contain"])
