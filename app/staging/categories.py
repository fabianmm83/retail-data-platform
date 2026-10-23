"""Modelo STAGING para categorías."""

import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Index,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class StagingCategory(Base):
    __tablename__ = "categories"
    __table_args__ = (
        CheckConstraint(
            "department IN ('APPAREL', 'FOOTWEAR', 'EQUIPMENT', 'ACCESSORIES')",
            name="stg_categories_department_check",
        ),
        CheckConstraint(
            "seasonality IN ('NONE', 'WINTER', 'NEW_YEAR', 'SUMMER')",
            name="stg_categories_seasonality_check",
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="stg_categories_status_check",
        ),
        Index("ix_stg_categories_department", "department"),
        {"schema": "staging"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[str] = mapped_column(String(20), nullable=False)
    seasonality: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    staged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )