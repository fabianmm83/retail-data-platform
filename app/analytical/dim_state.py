"""Dimensión estado geográfico."""

import uuid
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DimState(Base):
    """Los 10 estados de México."""

    __tablename__ = "dim_state"
    __table_args__ = (
        CheckConstraint(
            "region IN ('CENTRO', 'NORTE', 'OCCIDENTE', 'SUR')",
            name="dim_state_region_check",
        ),
        CheckConstraint(
            "income_group IN ('HIGH', 'MEDIUM', 'LOW')",
            name="dim_state_income_group_check",
        ),
        Index("ix_dim_state_region", "region"),
        Index("ix_dim_state_income_group", "income_group"),
        {"schema": "analytical"},
    )

    state_key: Mapped[int] = mapped_column(Integer, primary_key=True)
    state_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, unique=True
    )
    code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str] = mapped_column(String(20), nullable=False)
    income_group: Mapped[str] = mapped_column(String(20), nullable=False)
    population_share: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    online_penetration: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)