"""Chat endpoints: thread CRUD and streaming assistant turns."""

import asyncio
import json
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from supabase_auth.types import User

from app.auth.dependencies import get_current_user
from app.chat.orchestrator import run_turn
from app.database import chats
from app.database.supabase import get_service_role_client
from app.retrieval.retriever import DocumentRetriever

router = APIRouter(prefix="", tags=["chat"])


class CreateThreadRequest(BaseModel):
    title: str = Field(default="New Chat", max_length=255)


class ThreadResponse(BaseModel):
    id: int
    owner_id: str
    title: str
    created_at: str
    updated_at: str


class MessageResponse(BaseModel):
    id: int
    thread_id: int
    role: str
    content: str
    message_json: dict[str, Any]
    created_at: str


class StreamRequest(BaseModel):
    threadId: int | None = None
    id: int | None = None
    messages: list[dict[str, Any]] = Field(default_factory=list)

    @property
    def effective_thread_id(self) -> int:
        tid = self.threadId or self.id
        if not tid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="threadId is required",
            )
        return tid


def _verify_thread_access(client: Any, thread_id: int, user_id: str) -> dict[str, Any]:
    thread = chats.get_thread(client, thread_id)
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thread {thread_id} not found",
        )
    if str(thread.get("owner_id")) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this chat thread",
        )
    return thread


@router.get("/chats", response_model=list[ThreadResponse])
async def get_threads(
    user: Annotated[User, Depends(get_current_user)],
) -> list[dict[str, Any]]:
    client = get_service_role_client()
    return chats.list_threads(client, user.id)


@router.post("/chats", response_model=ThreadResponse, status_code=status.HTTP_201_CREATED)
async def create_new_thread(
    body: CreateThreadRequest,
    user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    client = get_service_role_client()
    return chats.create_thread(client, user.id, body.title)


@router.get("/chats/{thread_id}/messages", response_model=list[MessageResponse])
async def get_thread_messages(
    thread_id: int,
    user: Annotated[User, Depends(get_current_user)],
) -> list[dict[str, Any]]:
    client = get_service_role_client()
    _verify_thread_access(client, thread_id, user.id)
    return chats.list_messages(client, thread_id)


@router.post("/chat/stream")
async def chat_stream(
    body: StreamRequest,
    user: Annotated[User, Depends(get_current_user)],
):
    thread_id = body.effective_thread_id
    client = get_service_role_client()
    _verify_thread_access(client, thread_id, user.id)

    # Extract user's latest message
    latest_user_message = body.messages[-1] if body.messages else None
    user_content = ""
    if latest_user_message:
        # User message content in AI SDK can be a string or a list of parts
        content_val = latest_user_message.get("content", "")
        if isinstance(content_val, list):
            user_content = " ".join(
                part.get("text", "") for part in content_val if isinstance(part, dict) and "text" in part
            )
        elif isinstance(content_val, str):
            user_content = content_val
        elif "parts" in latest_user_message and isinstance(latest_user_message["parts"], list):
            user_content = " ".join(
                p.get("text", "") for p in latest_user_message["parts"] if isinstance(p, dict) and "text" in p
            )

        # Persist user message
        chats.save_message(
            client=client,
            thread_id=thread_id,
            role="user",
            content=user_content,
            message_json=latest_user_message,
        )

    retriever = DocumentRetriever()

    return StreamingResponse(
        run_turn(
            user_query=user_content,
            thread_id=thread_id,
            user_id=user.id,
            supabase_client=client,
            retriever=retriever,
        ),
        media_type="text/plain; charset=utf-8",
        headers={
            "x-vercel-ai-data-stream": "v1",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
