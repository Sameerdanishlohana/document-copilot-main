"""Document chunk model.

Retrieval-ready passages derived from a ``source_documents.content``. The
``embedding`` column is a pgvector ``vector(1536)`` and ``search_vector`` is a
generated Postgres ``tsvector`` column for full-text search.

The following are created explicitly in the Alembic migration rather than via
autogenerate: the ``vector`` extension, the generated ``tsvector`` expression,
the HNSW/GIN indexes, and RLS policies.
"""

from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("source_documents.id", ondelete="CASCADE"), index=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer)

    page: Mapped[str | None] = mapped_column(Text, nullable=True)
    section: Mapped[str | None] = mapped_column(Text, nullable=True)
    text: Mapped[str] = mapped_column(Text)
    token_count: Mapped[int] = mapped_column(Integer)

    embedding: Mapped[list[float]] = mapped_column(
        Vector(1536), nullable=True, comment="pgvector embedding (created in migration)"
    )

    # Metadata for ticker, company, filing type, filing date, year, accession
    # number, page, section, and source offsets. JSONB gives flexible filtering.
    # The Python attribute is ``meta`` because ``metadata`` is reserved by the
    # Declarative API; the DB column name stays ``metadata``.
    meta: Mapped[dict] = mapped_column("metadata", JSONB, server_default="{}")

    # Generated column; expression is created explicitly in the migration.
    search_vector: Mapped[object] = mapped_column(
        TSVECTOR, nullable=True, comment="generated tsvector for full-text search"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
