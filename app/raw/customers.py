"""Modelo RAW para clientes.

Copia fiel de `customers` del simulador.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.raw.mixins import RawMixin


class RawCustomer(RawMixin, Base):
    """Copia RAW de la tabla `customers` del simulador."""

    __tablename__ = "customers"
    __table_args__ = {"schema": "raw"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    customer_code: Mapped[str] = mapped_column(String(20), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    state_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(10), nullable=False)
    profile: Mapped[str] = mapped_column(String(20), nullable=False)
    channel_preference: Mapped[str] = mapped_column(String(20), nullable=False)
    preferred_segment: Mapped[str] = mapped_column(String(20), nullable=False)
    price_sensitivity: Mapped[str] = mapped_column(String(20), nullable=False)
    signup_date: Mapped[date] = mapped_column(Date, nullable=False)
    first_order_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_order_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    total_orders: Mapped[int] = mapped_column(Integer, nullable=False)
    total_revenue: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    total_units: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)