"""Chat orchestrator for Document Copilot.

Coordinates one complete conversational turn:
1. Prefetches top relevant 10-K passages using DocumentRetriever (hybrid pgvector + FTS + RRF)
2. Executes PydanticAI document_agent with GroundedAnswer output schema
3. Validates that all citations are grounded and non-hallucinated via validate_grounding
4. Emits AI SDK streaming events (text deltas + citations)
5. Persists the assistant turn and associated citations to Supabase
"""

import asyncio
from typing import AsyncGenerator
from supabase import Client

from app.assistant.generator import generate_grounded_answer
from app.assistant.outputs import GroundedAnswer
from app.chat.streaming import format_citations_data, format_finish_event, format_text_delta
from app.database import chats
from app.grounding.validator import validate_grounding
from app.retrieval.retriever import DocumentRetriever


async def run_turn(
    user_query: str,
    thread_id: int,
    user_id: str,
    supabase_client: Client,
    retriever: DocumentRetriever,
) -> AsyncGenerator[str, None]:
    """Execute one grounded research turn and stream events."""
    # 1. Hybrid prefetch (vector + FTS + RRF)
    retrieved_passages = retriever.search(query=user_query, top_k=6)

    # 2. Generate grounded answer with citations
    grounded_output: GroundedAnswer = await generate_grounded_answer(
        query=user_query,
        passages=retrieved_passages,
    )

    # 3. Fail-closed grounding validation
    validated_citations = validate_grounding(
        answer=grounded_output,
        allowed_chunks=retrieved_passages,
    )

    # 4. Stream response text deltas to the frontend in word chunks
    words = grounded_output.answer.split(" ")
    for idx, word in enumerate(words):
        chunk = word + (" " if idx < len(words) - 1 else "")
        yield format_text_delta(chunk)
        await asyncio.sleep(0.02)

    # 5. Emit citations part if available
    if validated_citations:
        yield format_citations_data(validated_citations)

    # 6. Persist assistant message and citations
    assistant_msg = chats.save_message(
        client=supabase_client,
        thread_id=thread_id,
        role="assistant",
        content=grounded_output.answer,
        message_json={
            "role": "assistant",
            "content": grounded_output.answer,
            "citations": [c.model_dump() for c in validated_citations],
            "insufficient_evidence": grounded_output.insufficient_evidence,
        },
    )

    if validated_citations:
        chats.save_citations(
            client=supabase_client,
            message_id=assistant_msg["id"],
            citations=[c.model_dump() for c in validated_citations],
        )

    chats.update_thread_timestamp(supabase_client, thread_id)

    # 7. Finish event
    yield format_finish_event()

