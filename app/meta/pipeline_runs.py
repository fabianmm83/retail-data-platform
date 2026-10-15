"""Modelo ORM para meta.pipeline_runs.

Cada corrida del pipeline genera un registro aquí. Permite rastrear:

- Cuándo empezó y terminó.
- Qué entidades se procesaron.
- Cuántas filas se ingestaron por entidad.
- Si hubo errores.
"""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PipelineRun(Base):
    """Registro de cada corrida del pipeline."""

    __tablename__ = "pipeline_runs"
    __table_args__ = {"schema": "meta"}

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    run_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        comment="ING-YYYYMMDD-HHMMSS-8hex",
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="RUNNING",
        comment="RUNNING | SUCCESS | FAILED",
    )

    entities_processed: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="CSV de entidades procesadas",
    )

    rows_ingested: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )