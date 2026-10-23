"""Modelo STAGING para variantes de producto (SKUs)."""

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


class StagingProductVariant(Base):
    __tablename__ = "product_variants"
    __table_args__ = (
        CheckConstraint(
            "color IN ('BLK', 'WHT', 'GRY', 'NVY', 'RED', 'BLU', 'GRN', 'PNK', 'YLW')",
            name="stg_variants_color_check",
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="stg_variants_status_check",
        ),
        CheckConstraint(
            "length(size) > 0",
            name="stg_variants_size_nonempty",
        ),
        Index("ix_stg_variants_product", "product_id"),
        Index("ix_stg_variants_color", "color"),
        Index("ix_stg_variants_size", "size"),
        {"schema": "staging"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    sku: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    size: Mapped[str] = mapped_column(String(10), nullable=False)
    color: Mapped[str] = mapped_column(String(10), nullable=False)
    barcode: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    staged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )