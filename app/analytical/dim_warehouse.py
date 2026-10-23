"""Dimensión ubicación (CEDIS + tiendas)."""

import uuid

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DimWarehouse(Base):
    """Ubicaciones físicas."""

    __tablename__ = "dim_warehouse"
    __table_args__ = (
        CheckConstraint(
            "location_type IN ('CEDIS', 'STORE')",
            name="dim_warehouse_type_check",
        ),
        Index("ix_dim_warehouse_type", "location_type"),
        Index("ix_dim_warehouse_state", "state_key"),
        {"schema": "analytical"},
    )

    warehouse_key: Mapped[int] = mapped_column(Integer, primary_key=True)
    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, unique=True
    )
    code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    location_type: Mapped[str] = mapped_column(String(20), nullable=False)
    state_key: Mapped[int] = mapped_column(
        ForeignKey("analytical.dim_state.state_key"), nullable=False
    )