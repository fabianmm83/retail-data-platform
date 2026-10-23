"""KPI: revenue por estado × mes."""

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


class KpiRevenueByState(Base):
    """Revenue agregado por estado × mes."""

    __tablename__ = "revenue_by_state"
    __table_args__ = (
        CheckConstraint("revenue >= 0", name="kpi_rev_state_revenue_nonneg"),
        CheckConstraint("units >= 0", name="kpi_rev_state_units_nonneg"),
        CheckConstraint("orders >= 0", name="kpi_rev_state_orders_nonneg"),
        Index("ix_kpi_rev_state_state", "state_key"),
        Index("ix_kpi_rev_state_year_month", "year", "month"),
        {"schema": "kpis"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    state_key: Mapped[int] = mapped_column(
        ForeignKey("analytical.dim_state.state_key"), nullable=False
    )
    state_code: Mapped[str] = mapped_column(String(10), nullable=False)
    state_name: Mapped[str] = mapped_column(String(100), nullable=False)

    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)

    revenue: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    units: Mapped[int] = mapped_column(Integer, nullable=False)
    orders: Mapped[int] = mapped_column(Integer, nullable=False)
    aov: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)