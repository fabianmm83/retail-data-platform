"""Modelo RAW para movimientos de inventario.

Copia fiel de `inventory_movements` del simulador.
"""

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.raw.mixins import RawMixin


class RawInventoryMovement(RawMixin, Base):
    """Copia RAW de la tabla `inventory_movements` del simulador."""

    __tablename__ = "inventory_movements"
    __table_args__ = {"schema": "raw"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    variant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    location_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    movement_type: Mapped[str] = mapped_column(String(30), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    reference_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    reference_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    movement_date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)