"""AI SDK UI Message SSE stream serialization utilities for Document Copilot."""

import json
from typing import Any
from app.assistant.outputs import Citation


def format_stream_start() -> str:
    """Format start events for UI Message stream."""
    return 'data: {"type":"start"}\n\ndata: {"type":"start-step"}\n\n'


def format_text_start(text_id: str = "text-1") -> str:
    """Format text-start event."""
    return f'data: {{"type":"text-start","id":{json.dumps(text_id)}}}\n\n'


def format_text_delta(chunk: str, text_id: str = "text-1") -> str:
    """Format a text delta in the AI SDK UI Message stream (data: {"type":"text-delta",...})."""
    payload = json.dumps({"type": "text-delta", "id": text_id, "delta": chunk})
    return f"data: {payload}\n\n"


def format_text_end(text_id: str = "text-1") -> str:
    """Format text-end event."""
    return f'data: {{"type":"text-end","id":{json.dumps(text_id)}}}\n\n'


def format_citations_data(citations: list[Citation]) -> str:
    """Format citations as custom UI message data."""
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
    payload = json.dumps({
        "type": "data-citations",
        "data": {
            "type": "citations",
            "citations": citation_dicts,
        },
    })
    return f"data: {payload}\n\n"


def format_finish_event() -> str:
    """Format the completion event sequence for the AI SDK UI message stream."""
    return 'data: {"type":"finish-step"}\n\ndata: {"type":"finish"}\n\n'


