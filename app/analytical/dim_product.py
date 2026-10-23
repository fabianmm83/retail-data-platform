"""Dimensión producto."""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DimProduct(Base):
    """Productos (style codes)."""

    __tablename__ = "dim_product"
    __table_args__ = (
        CheckConstraint(
            "segment IN ('WOMEN', 'MEN', 'KIDS', 'UNISEX')",
            name="dim_product_segment_check",
        ),
        CheckConstraint(
            "demand_profile IN ('HIGH', 'MEDIUM', 'LOW', 'NICHE')",
            name="dim_product_demand_check",
        ),
        CheckConstraint(
            "lifecycle_stage IN ('LAUNCH', 'GROWTH', 'MATURE', 'DECLINE', 'DISCONTINUED')",
            name="dim_product_lifecycle_check",
        ),
        Index("ix_dim_product_segment", "segment"),
        Index("ix_dim_product_branded", "branded"),
        Index("ix_dim_product_demand", "demand_profile"),
        {"schema": "analytical"},
    )

    product_key: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, unique=True
    )
    style_code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    segment: Mapped[str] = mapped_column(String(20), nullable=False)
    age_group: Mapped[str] = mapped_column(String(20), nullable=False)
    sport: Mapped[str] = mapped_column(String(20), nullable=False)
    branded: Mapped[bool] = mapped_column(Boolean, nullable=False)
    base_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    base_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    demand_profile: Mapped[str] = mapped_column(String(20), nullable=False)
    lifecycle_stage: Mapped[str] = mapped_column(String(20), nullable=False)
    launch_date: Mapped[date] = mapped_column(Date, nullable=False)