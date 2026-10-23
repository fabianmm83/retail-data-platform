"""Hecho de shipments.

Grano: 1 fila = 1 shipment.
"""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FactShipments(Base):
    """Hecho de shipments."""

    __tablename__ = "fact_shipments"
    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'PACKED', 'SHIPPED', 'IN_TRANSIT', "
            "'OUT_FOR_DELIVERY', 'DELIVERED', 'DELAYED', 'LOST')",
            name="fact_shipments_status_check",
        ),
        CheckConstraint(
            "shipping_cost >= 0 AND weight_kg >= 0",
            name="fact_shipments_amounts_nonnegative",
        ),
        Index("ix_fact_shipments_date", "date_key"),
        Index("ix_fact_shipments_order", "order_id"),
        Index("ix_fact_shipments_warehouse", "warehouse_key"),
        Index("ix_fact_shipments_status", "status"),
        {"schema": "analytical"},
    )

    shipment_key: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )

    date_key: Mapped[int] = mapped_column(
        ForeignKey("analytical.dim_date.date_key"), nullable=False
    )
    warehouse_key: Mapped[int] = mapped_column(
        ForeignKey("analytical.dim_warehouse.warehouse_key"), nullable=False
    )

    # Business keys
    shipment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    shipment_number: Mapped[str] = mapped_column(String(30), nullable=False)
    tracking_number: Mapped[str] = mapped_column(String(50), nullable=False)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    status: Mapped[str] = mapped_column(String(30), nullable=False)

    # Fechas
    shipped_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    estimated_delivery: Mapped[date | None] = mapped_column(Date, nullable=True)
    delivered_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Lead time calculado (días)
    lead_time_days: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="delivered_at - shipped_at en días (NULL si no entregado)",
    )
    is_on_time: Mapped[bool | None] = mapped_column(
        nullable=True,
        comment="delivered_at <= estimated_delivery (NULL si no entregado)",
    )

    # Medidas
    shipping_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(8, 3), nullable=False)

    loaded_at: Mapped[date | None] = mapped_column(
        Date, nullable=True, server_default=func.current_date()
    )