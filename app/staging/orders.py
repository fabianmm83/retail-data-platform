"""Modelo STAGING para órdenes.

Datos limpios y tipados de raw.orders.

Diferencias respecto a RAW:
- Enums como String + CHECK constraint.
- Sin metadata de ingesta.
- Columna derivada: line_count (número de items).
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Index,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class StagingOrder(Base):
    """Orden limpia y tipada."""

    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint(
            "channel IN ('ONLINE', 'STORE')",
            name="stg_orders_channel_check",
        ),
        CheckConstraint(
            "status IN ('PENDING', 'CONFIRMED', 'PROCESSING', 'PACKED', 'SHIPPED', "
            "'IN_TRANSIT', 'DELIVERED', 'CANCELLED', 'RETURNED')",
            name="stg_orders_status_check",
        ),
        CheckConstraint(
            "payment_method IN ('CARD', 'CASH', 'TRANSFER', 'OXXO', 'WALLET')",
            name="stg_orders_payment_check",
        ),
        CheckConstraint(
            "subtotal >= 0 AND discount >= 0 AND shipping_cost >= 0 AND total >= 0",
            name="stg_orders_amounts_nonnegative",
        ),
        CheckConstraint(
            "discount <= subtotal",
            name="stg_orders_discount_lte_subtotal",
        ),
        Index("ix_stg_orders_customer", "customer_id"),
        Index("ix_stg_orders_state", "state_id"),
        Index("ix_stg_orders_location", "location_id"),
        Index("ix_stg_orders_channel", "channel"),
        Index("ix_stg_orders_status", "status"),
        Index("ix_stg_orders_date", "order_date"),
        {"schema": "staging"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        comment="Mismo UUID del origen",
    )

    order_number: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    state_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    location_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_method: Mapped[str] = mapped_column(String(20), nullable=False)
    paid: Mapped[bool] = mapped_column(Boolean, nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    shipping_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    line_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
        comment="Número de items en la orden (derivado)",
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    staged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )