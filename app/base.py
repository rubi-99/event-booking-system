from datetime import datetime, timezone
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func, DateTime

# The main registry base class
class Base(DeclarativeBase):
    pass

# Reusable mixin for automatic auditing timestamps
class TimestampMixin:
    # Mapped[datetime] specifies that this attribute maps to a SQL TIMESTAMP.
    # We specify DateTime(timezone=True) so Postgres uses TIMESTAMP WITH TIME ZONE (TIMESTAMPTZ),
    # which is required to store timezone-aware UTC datetimes.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now()
    )
    
    # onupdate is run on the Python side whenever we update the record.
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc)
    )
