"""Hecho de ventas.

Grano: 1 fila = 1 línea de orden (item).
"""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
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


class FactSales(Base):
    """Hecho de ventas: 1 fila por línea de orden."""

    __tablename__ = "fact_sales"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="fact_sales_quantity_positive"),
        CheckConstraint(
            "unit_price >= 0 AND discount >= 0 AND subtotal >= 0",
            name="fact_sales_amounts_nonnegative",
        ),
        CheckConstraint(
            "channel IN ('ONLINE', 'STORE')",
            name="fact_sales_channel_check",
        ),
        Index("ix_fact_sales_date", "date_key"),
        Index("ix_fact_sales_customer", "customer_key"),
        Index("ix_fact_sales_product", "product_key"),
        Index("ix_fact_sales_variant", "variant_key"),
        Index("ix_fact_sales_state", "state_key"),
        Index("ix_fact_sales_warehouse", "warehouse_key"),
        Index("ix_fact_sales_order", "order_id"),
        Index("ix_fact_sales_channel", "channel"),
        {"schema": "analytical"},
    )

    sale_key: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # FKs a dimensiones
    date_key: Mapped[int] = mapped_column(
        ForeignKey("analytical.dim_date.date_key"), nullable=False
    )
    customer_key: Mapped[int] = mapped_column(
        ForeignKey("analytical.dim_customer.customer_key"), nullable=False
    )
    product_key: Mapped[int] = mapped_column(
        ForeignKey("analytical.dim_product.product_key"), nullable=False
    )
    variant_key: Mapped[int] = mapped_column(
        ForeignKey("analytical.dim_variant.variant_key"), nullable=False
    )
    state_key: Mapped[int] = mapped_column(
        ForeignKey("analytical.dim_state.state_key"), nullable=False
    )
    warehouse_key: Mapped[int] = mapped_column(
        ForeignKey("analytical.dim_warehouse.warehouse_key"), nullable=False
    )

    # Business keys (para trazabilidad)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    order_number: Mapped[str] = mapped_column(String(30), nullable=False)
    channel: Mapped[str] = mapped_column(String(20), nullable=False)

    # Medidas
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    discount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, server_default="0")
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    # Auditoría
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    loaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )