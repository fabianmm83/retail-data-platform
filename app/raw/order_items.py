"""Modelo RAW para order items.

Copia fiel de `order_items` del simulador.
"""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.raw.mixins import RawMixin


class RawOrderItem(RawMixin, Base):
    """Copia RAW de la tabla `order_items` del simulador."""

    __tablename__ = "order_items"
    __table_args__ = {"schema": "raw"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    variant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    discount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)