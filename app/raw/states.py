"""Modelo RAW para estados."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.raw.mixins import RawMixin


class RawState(RawMixin, Base):
    __tablename__ = "states"
    __table_args__ = {"schema": "raw"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    code: Mapped[str] = mapped_column(String(10), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str] = mapped_column(String(20), nullable=False)
    income_group: Mapped[str] = mapped_column(String(20), nullable=False)
    population_share: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    income_index: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    online_penetration: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    regional_factor: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    growth_rate: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)