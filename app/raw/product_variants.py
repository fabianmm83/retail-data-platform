"""Modelo RAW para variantes de producto (SKUs).

Copia fiel de `product_variants` del simulador.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.raw.mixins import RawMixin


class RawProductVariant(RawMixin, Base):
    """Copia RAW de la tabla `product_variants` del simulador."""

    __tablename__ = "product_variants"
    __table_args__ = {"schema": "raw"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    sku: Mapped[str] = mapped_column(String(50), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    size: Mapped[str] = mapped_column(String(10), nullable=False)
    color: Mapped[str] = mapped_column(String(10), nullable=False)
    barcode: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)