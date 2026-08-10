"""SQLAlchemy models for Document Copilot.

Importing every model module here populates ``Base.metadata`` so that Alembic
autogenerate sees the full schema. Alembic ``env.py`` should import this package
(or ``Base`` from here) as the source of truth for ``target_metadata``.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base shared by all application models."""

    # SQLAlchemy auto-creates ``Base.metadata`` when subclassing DeclarativeBase.


# Import models after Base is defined so each module binds to the same base.
# The imports are intentionally unused at runtime; they register the tables on
# Base.metadata so Alembic autogenerate sees the full schema.
from app.database.models import (  # noqa: E402, F401  (imported for metadata)
    chat_messages,
    chat_threads,
    document_chunks,
    message_citations,
    profiles,
    source_documents,
)

__all__ = [
    "Base",
    "Profile",
    "SourceDocument",
    "DocumentChunk",
    "ChatThread",
    "ChatMessage",
    "MessageCitation",
]
