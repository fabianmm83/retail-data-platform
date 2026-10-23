"""Modelo STAGING para shipments."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Index,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class StagingShipment(Base):
    __tablename__ = "shipments"
    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'PACKED', 'SHIPPED', 'IN_TRANSIT', "
            "'OUT_FOR_DELIVERY', 'DELIVERED', 'DELAYED', 'LOST')",
            name="stg_shipments_status_check",
        ),
        CheckConstraint(
            "shipping_cost >= 0 AND weight_kg >= 0",
            name="stg_shipments_amounts_nonnegative",
        ),
        CheckConstraint(
            "shipped_at IS NULL OR estimated_delivery IS NULL "
            "OR estimated_delivery >= shipped_at",
            name="stg_shipments_estimated_after_shipped",
        ),
        CheckConstraint(
            "delivered_at IS NULL OR shipped_at IS NULL "
            "OR delivered_at >= shipped_at",
            name="stg_shipments_delivered_after_shipped",
        ),
        Index("ix_stg_shipments_order", "order_id"),
        Index("ix_stg_shipments_carrier", "carrier_id"),
        Index("ix_stg_shipments_origin", "origin_location_id"),
        Index("ix_stg_shipments_status", "status"),
        Index("ix_stg_shipments_shipped_at", "shipped_at"),
        {"schema": "staging"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, comment="Mismo UUID del origen"
    )
    shipment_number: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    tracking_number: Mapped[str] = mapped_column(String(50), nullable=False)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    carrier_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    origin_location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    shipped_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    estimated_delivery: Mapped[date | None] = mapped_column(Date, nullable=True)
    delivered_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    shipping_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(8, 3), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    staged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )