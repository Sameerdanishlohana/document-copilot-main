"""Source document model.

A single SEC filing that has been ingested and normalized to Markdown. The
normalized ``content`` is stored so the app can re-chunk, inspect, and cite the
extracted text without reaching back into downloaded HTML files.
"""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models import Base


class SourceDocument(Base):
    __tablename__ = "source_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    ticker: Mapped[str] = mapped_column(String(16), index=True)
    company: Mapped[str] = mapped_column(String(255))
    filing_type: Mapped[str] = mapped_column(String(32), index=True)
    fiscal_year: Mapped[int] = mapped_column(Integer, index=True)
    filing_date: Mapped[date] = mapped_column(Date)
    accession_number: Mapped[str] = mapped_column(String(64), unique=True)
    source_url: Mapped[str] = mapped_column(String(1024))
    content: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
