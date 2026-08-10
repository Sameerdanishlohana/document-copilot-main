"""Profile model.

One row per authenticated user, keyed by Supabase ``auth.users.id``. All chat
records and citations are scoped to a profile's ``id``.
"""

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models import Base


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        # Matches Supabase auth.users.id; Postgres casts the incoming uuid to text.
        comment="Supabase auth.users.id",
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
