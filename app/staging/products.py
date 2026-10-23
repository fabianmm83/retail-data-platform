"""Modelo STAGING para productos."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
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


class StagingProduct(Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint(
            "segment IN ('WOMEN', 'MEN', 'KIDS', 'UNISEX')",
            name="stg_products_segment_check",
        ),
        CheckConstraint(
            "age_group IN ('ADULT', 'KIDS')",
            name="stg_products_age_group_check",
        ),
        CheckConstraint(
            "sport IN ('RUNNING', 'TRAINING', 'FUTBOL', 'BASKET', 'CASUAL', 'YOGA', 'GENERAL')",
            name="stg_products_sport_check",
        ),
        CheckConstraint(
            "demand_profile IN ('HIGH', 'MEDIUM', 'LOW', 'NICHE')",
            name="stg_products_demand_profile_check",
        ),
        CheckConstraint(
            "lifecycle_stage IN ('LAUNCH', 'GROWTH', 'MATURE', 'DECLINE', 'DISCONTINUED')",
            name="stg_products_lifecycle_check",
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="stg_products_status_check",
        ),
        CheckConstraint(
            "base_price > 0 AND base_cost > 0 AND base_price > base_cost",
            name="stg_products_prices_check",
        ),
        Index("ix_stg_products_category", "category_id"),
        Index("ix_stg_products_segment", "segment"),
        Index("ix_stg_products_demand", "demand_profile"),
        {"schema": "staging"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    style_code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    segment: Mapped[str] = mapped_column(String(20), nullable=False)
    age_group: Mapped[str] = mapped_column(String(20), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    sport: Mapped[str] = mapped_column(String(20), nullable=False)
    branded: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    base_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    base_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    demand_profile: Mapped[str] = mapped_column(String(20), nullable=False)
    lifecycle_stage: Mapped[str] = mapped_column(String(20), nullable=False)
    launch_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    staged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )