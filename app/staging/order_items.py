"""Modelo STAGING para order_items.

Datos limpios y tipados de raw.order_items.
Sin enums, así que no necesita CHECK constraints de enums.
"""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Index,
    Integer,
    Numeric,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class StagingOrderItem(Base):
    """Item de orden limpio y tipado."""

    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="stg_order_items_quantity_positive",
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="stg_order_items_unit_price_nonnegative",
        ),
        CheckConstraint(
            "discount >= 0",
            name="stg_order_items_discount_nonnegative",
        ),
        CheckConstraint(
            "subtotal >= 0",
            name="stg_order_items_subtotal_nonnegative",
        ),
        Index("ix_stg_order_items_order", "order_id"),
        Index("ix_stg_order_items_variant", "variant_id"),
        {"schema": "staging"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        comment="Mismo UUID del origen",
    )

    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    variant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    discount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    staged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )