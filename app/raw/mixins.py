"""Mixin común para todos los modelos RAW.

Cada tabla RAW tiene:

- La PK del origen (`_source_id`).
- Metadata de ingesta (`_ingested_at`, `_ingestion_run_id`, `_source_table`).
- Un ID técnico propio (`_raw_id`) que es BIGSERIAL.
"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class RawMixin:
    """Metadata común a todas las tablas RAW."""

    _raw_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    _source_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        unique=True,
        comment="UUID de la fila en la tabla origen (idempotencia)",
    )

    _ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    _ingestion_run_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    _source_table: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )