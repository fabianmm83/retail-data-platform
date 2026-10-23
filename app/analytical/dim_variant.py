"""Dimensión variante (SKU)."""

import uuid

from sqlalchemy import (
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DimVariant(Base):
    """Variantes de producto (SKU = talla × color)."""

    __tablename__ = "dim_variant"
    __table_args__ = (
        Index("ix_dim_variant_product", "product_key"),
        Index("ix_dim_variant_color", "color"),
        Index("ix_dim_variant_size", "size"),
        {"schema": "analytical"},
    )

    variant_key: Mapped[int] = mapped_column(Integer, primary_key=True)
    variant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, unique=True
    )
    sku: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    product_key: Mapped[int] = mapped_column(
        ForeignKey("analytical.dim_product.product_key"), nullable=False
    )
    size: Mapped[str] = mapped_column(String(10), nullable=False)
    color: Mapped[str] = mapped_column(String(10), nullable=False)