"""Modelo STAGING para ubicaciones."""

import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class StagingLocation(Base):
    __tablename__ = "locations"
    __table_args__ = (
        CheckConstraint(
            "location_type IN ('CEDIS', 'STORE')",
            name="stg_locations_type_check",
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="stg_locations_status_check",
        ),
        CheckConstraint(
            "capacity_units >= 0",
            name="stg_locations_capacity_nonnegative",
        ),
        Index("ix_stg_locations_state", "state_id"),
        Index("ix_stg_locations_type", "location_type"),
        {"schema": "staging"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    location_type: Mapped[str] = mapped_column(String(20), nullable=False)
    state_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    capacity_units: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    staged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )