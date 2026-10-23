"""KPI: revenue por producto × mes."""

from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class KpiRevenueByProduct(Base):
    """Revenue agregado por producto × mes."""

    __tablename__ = "revenue_by_product"
    __table_args__ = (
        CheckConstraint("revenue >= 0", name="kpi_rev_prod_revenue_nonneg"),
        CheckConstraint("units >= 0", name="kpi_rev_prod_units_nonneg"),
        CheckConstraint("orders >= 0", name="kpi_rev_prod_orders_nonneg"),
        Index("ix_kpi_rev_prod_product", "product_key"),
        Index("ix_kpi_rev_prod_year_month", "year", "month"),
        {"schema": "kpis"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    product_key: Mapped[int] = mapped_column(
        ForeignKey("analytical.dim_product.product_key"), nullable=False
    )
    style_code: Mapped[str] = mapped_column(String(30), nullable=False)
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)

    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)

    revenue: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    units: Mapped[int] = mapped_column(Integer, nullable=False)
    orders: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)