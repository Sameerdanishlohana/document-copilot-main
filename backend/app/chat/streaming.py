"""AI SDK data stream serialization utilities for Document Copilot."""

import json
from typing import Any
from app.assistant.outputs import Citation


def format_text_delta(chunk: str) -> str:
    """Format a text delta in the Vercel AI SDK Data Stream protocol (0:"text")."""
    return f"0:{json.dumps(chunk)}\n"


def format_citations_data(citations: list[Citation]) -> str:
    """Format structured citation objects as a custom data part (2:[...]) for the AI SDK."""
    citation_dicts = [
        {
            "chunk_id": c.chunk_id,
            "company": c.company,
            "filing_type": c.filing_type,
            "filing_date": c.filing_date,
            "page": c.page,
            "section": c.section,
            "excerpt": c.excerpt,
        }
        for c in citations
    ]
    payload = json.dumps([{"type": "citations", "citations": citation_dicts}])
    return f"2:{payload}\n"


def format_finish_event(finish_reason: str = "stop", usage: dict[str, Any] | None = None) -> str:
    """Format the completion event part (d:{...}) for the AI SDK data stream."""
    payload = json.dumps({
        "finishReason": finish_reason,
        "usage": usage or {"promptTokens": 0, "completionTokens": 0},
    })
    return f"d:{payload}\n"

