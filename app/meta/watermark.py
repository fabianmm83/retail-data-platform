"""Modelo ORM para meta.watermarks.

Un watermark por entidad. Registra hasta dónde se ha ingestado cada
tabla del origen.

- `last_watermark_date`: fecha simulada del último registro ingestado.
- `last_watermark_id`: UUID del último registro ingestado (por si dos
  registros comparten fecha).
- `last_run_at`: cuándo corrió la ingesta por última vez (timestamp real).
- `rows_last_run`: cuántas filas se trajeron en la última corrida.
- `status`: SUCCESS | FAILED | RUNNING.
"""

from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Watermark(Base):
    """Registro de control de ingesta por entidad."""

    __tablename__ = "watermarks"
    __table_args__ = {"schema": "meta"}

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    entity_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        comment="Nombre lógico: orders, customers, inventory_movements",
    )

    last_watermark_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        comment="Fecha simulada del último registro ingestado",
    )

    last_watermark_id: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="ID del último registro ingestado (para desempate)",
    )

    last_run_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp real de la última corrida",
    )

    rows_last_run: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="SUCCESS",
        comment="SUCCESS | FAILED | RUNNING",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )