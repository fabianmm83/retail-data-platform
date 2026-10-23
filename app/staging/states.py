"""Modelo STAGING para estados."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Index,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class StagingState(Base):
    __tablename__ = "states"
    __table_args__ = (
        CheckConstraint(
            "region IN ('CENTRO', 'NORTE', 'OCCIDENTE', 'SUR')",
            name="stg_states_region_check",
        ),
        CheckConstraint(
            "income_group IN ('HIGH', 'MEDIUM', 'LOW')",
            name="stg_states_income_group_check",
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="stg_states_status_check",
        ),
        CheckConstraint(
            "population_share >= 0 AND population_share <= 1",
            name="stg_states_population_share_range",
        ),
        CheckConstraint(
            "online_penetration >= 0 AND online_penetration <= 1",
            name="stg_states_online_penetration_range",
        ),
        Index("ix_stg_states_region", "region"),
        Index("ix_stg_states_income_group", "income_group"),
        {"schema": "staging"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str] = mapped_column(String(20), nullable=False)
    income_group: Mapped[str] = mapped_column(String(20), nullable=False)
    population_share: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    income_index: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    online_penetration: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    regional_factor: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    growth_rate: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    staged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )