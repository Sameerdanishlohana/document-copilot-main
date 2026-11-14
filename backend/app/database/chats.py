"""Chat database persistence helper.

Handles thread CRUD and message loading/persisting using the Supabase client.
"""

from typing import Any
from supabase import Client


def list_threads(client: Client, owner_id: str) -> list[dict[str, Any]]:
    """List all chat threads for a user, ordered by most recently updated."""
    response = (
        client.table("chat_threads")
        .select("*")
        .eq("owner_id", owner_id)
        .order("updated_at", desc=True)
        .execute()
    )
    return response.data or []


def create_thread(client: Client, owner_id: str, title: str) -> dict[str, Any]:
    """Create a new chat thread owned by owner_id."""
    response = (
        client.table("chat_threads")
        .insert({"owner_id": owner_id, "title": title})
        .execute()
    )
    if not response.data:
        raise RuntimeError("Failed to create chat thread")
    return response.data[0]


def get_thread(client: Client, thread_id: int) -> dict[str, Any] | None:
    """Fetch a single thread by id."""
    response = (
        client.table("chat_threads")
        .select("*")
        .eq("id", thread_id)
        .maybe_single()
        .execute()
    )
    return response.data


def list_messages(client: Client, thread_id: int) -> list[dict[str, Any]]:
    """Fetch all messages for a thread in chronological order."""
    response = (
        client.table("chat_messages")
        .select("*")
        .eq("thread_id", thread_id)
        .order("created_at", desc=False)
        .execute()
    )
    return response.data or []


def save_message(
    client: Client,
    thread_id: int,
    role: str,
    content: str,
    message_json: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Persist a single user or assistant message to a thread."""
    payload = {
        "thread_id": thread_id,
        "role": role,
        "content": content,
        "message_json": message_json or {},
    }
    response = client.table("chat_messages").insert(payload).execute()
    if not response.data:
        raise RuntimeError("Failed to save message")
    return response.data[0]


def save_citations(
    client: Client,
    message_id: int,
    citations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Persist normalized citation records associated with an assistant message."""
    if not citations:
        return []

    rows = []
    for c in citations:
        rows.append(
            {
                "message_id": message_id,
                "chunk_id": c.get("chunk_id"),
                "company": c.get("company", ""),
                "filing_type": c.get("filing_type", "10-K"),
                "filing_date": c.get("filing_date"),
                "page": c.get("page"),
                "section": c.get("section"),
                "excerpt": c.get("excerpt", ""),
            }
        )

    response = client.table("message_citations").insert(rows).execute()
    return response.data or []


def list_message_citations(client: Client, message_id: int) -> list[dict[str, Any]]:
    """Fetch citations for a given message."""
    response = (
        client.table("message_citations")
        .select("*")
        .eq("message_id", message_id)
        .order("id", desc=False)
        .execute()
    )
    return response.data or []


def update_thread_timestamp(client: Client, thread_id: int) -> None:
    """Update updated_at on chat_threads to bump active conversations."""
    client.table("chat_threads").update({"updated_at": "now()"}).eq("id", thread_id).execute()


