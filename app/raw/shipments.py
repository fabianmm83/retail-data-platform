"""Modelo RAW para envíos."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.raw.mixins import RawMixin


class RawShipment(RawMixin, Base):
    __tablename__ = "shipments"
    __table_args__ = {"schema": "raw"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    shipment_number: Mapped[str] = mapped_column(String(30), nullable=False)
    tracking_number: Mapped[str] = mapped_column(String(50), nullable=False)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    carrier_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    origin_location_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    shipped_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    estimated_delivery: Mapped[date | None] = mapped_column(Date, nullable=True)
    delivered_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    shipping_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(8, 3), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)