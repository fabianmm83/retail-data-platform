"""Modelo RAW para carriers."""

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


class RawCarrier(RawMixin, Base):
    __tablename__ = "carriers"
    __table_args__ = {"schema": "raw"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    carrier_code: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    coverage: Mapped[str] = mapped_column(String(20), nullable=False)
    base_lead_time_days: Mapped[int] = mapped_column(Integer, nullable=False)
    max_lead_time_days: Mapped[int] = mapped_column(Integer, nullable=False)
    reliability: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    base_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    cost_multiplier: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)