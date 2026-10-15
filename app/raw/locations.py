"""Modelo RAW para ubicaciones (CEDIS + tiendas)."""

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.raw.mixins import RawMixin


class RawLocation(RawMixin, Base):
    __tablename__ = "locations"
    __table_args__ = {"schema": "raw"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    code: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    location_type: Mapped[str] = mapped_column(String(20), nullable=False)
    state_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    capacity_units: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)