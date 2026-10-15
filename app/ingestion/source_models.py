"""Modelos ORM del ORIGEN (simulador).

El data platform NO importa el código del simulador. En su lugar,
define modelos locales que apuntan a las tablas del origen.

Estos modelos son SOLO LECTURA. Nunca se escriben.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum as SAEnum,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class SourceBase(DeclarativeBase):
    """Base declarativa para modelos del origen."""
    pass


# =============================================================================
# CUSTOMERS
# =============================================================================


class Customer(SourceBase):
    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    customer_code: Mapped[str] = mapped_column(String(20))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(200))
    phone: Mapped[str] = mapped_column(String(20))
    birth_date: Mapped[date] = mapped_column(Date)
    gender: Mapped[str] = mapped_column(String(20))
    state_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    city: Mapped[str] = mapped_column(String(100))
    postal_code: Mapped[str] = mapped_column(String(10))
    profile: Mapped[str] = mapped_column(String(20))
    channel_preference: Mapped[str] = mapped_column(String(20))
    preferred_segment: Mapped[str] = mapped_column(String(20))
    price_sensitivity: Mapped[str] = mapped_column(String(20))
    signup_date: Mapped[date] = mapped_column(Date)
    first_order_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_order_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    total_orders: Mapped[int] = mapped_column(Integer)
    total_revenue: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    total_units: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


# =============================================================================
# ORDERS
# =============================================================================


class Order(SourceBase):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    order_number: Mapped[str] = mapped_column(String(30))
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    state_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    location_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    channel: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20))
    order_date: Mapped[date] = mapped_column(Date)
    payment_method: Mapped[str] = mapped_column(String(20))
    paid: Mapped[bool] = mapped_column(Boolean)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    discount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    shipping_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


# =============================================================================
# ORDER ITEMS
# =============================================================================


class OrderItem(SourceBase):
    __tablename__ = "order_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    variant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    discount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))