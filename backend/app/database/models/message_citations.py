"""Message citation model.

Normalized citation record linked to an assistant message. Each citation points
to the source document chunk that supports the claim, plus enough denormalized
metadata for the frontend to render company, filing, date, page, and section
without a join.
"""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models import Base


class MessageCitation(Base):
    __tablename__ = "message_citations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    message_id: Mapped[int] = mapped_column(
        ForeignKey("chat_messages.id", ondelete="CASCADE"), index=True
    )

    # Optional link to the retrieved chunk that backs this citation.
    chunk_id: Mapped[int | None] = mapped_column(
        ForeignKey("document_chunks.id", ondelete="SET NULL"), nullable=True
    )

    company: Mapped[str] = mapped_column(Text)
    filing_type: Mapped[str] = mapped_column(Text)
    filing_date: Mapped[date] = mapped_column(Date)
    page: Mapped[str | None] = mapped_column(Text, nullable=True)
    section: Mapped[str | None] = mapped_column(Text, nullable=True)
    excerpt: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
