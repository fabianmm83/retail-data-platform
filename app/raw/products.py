"""Modelo RAW para productos.

Copia fiel de `products` del simulador.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.raw.mixins import RawMixin


class RawProduct(RawMixin, Base):
    """Copia RAW de la tabla `products` del simulador."""

    __tablename__ = "products"
    __table_args__ = {"schema": "raw"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    style_code: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    segment: Mapped[str] = mapped_column(String(20), nullable=False)
    age_group: Mapped[str] = mapped_column(String(20), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    sport: Mapped[str] = mapped_column(String(20), nullable=False)
    branded: Mapped[bool] = mapped_column(Boolean, nullable=False)
    base_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    base_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    demand_profile: Mapped[str] = mapped_column(String(20), nullable=False)
    lifecycle_stage: Mapped[str] = mapped_column(String(20), nullable=False)
    launch_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)