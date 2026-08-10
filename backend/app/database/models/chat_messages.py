"""Chat message model.

One row per user or assistant message in a thread, kept in insertion order.
``message_json`` stores the AI SDK-compatible message payload for round-tripping
with the frontend chat client.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    thread_id: Mapped[int] = mapped_column(
        ForeignKey("chat_threads.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[str] = mapped_column(Text)  # "user" | "assistant"
    content: Mapped[str] = mapped_column(Text)
    message_json: Mapped[dict] = mapped_column(JSONB, server_default="{}")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
