"""KPI: revenue diario.

Grano: 1 fila = 1 día × 1 estado × 1 canal × 1 categoría.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class KpiRevenueDaily(Base):
    """Revenue agregado por día × estado × canal × categoría."""

    __tablename__ = "revenue_daily"
    __table_args__ = (
        CheckConstraint("revenue >= 0", name="kpi_rev_daily_revenue_nonneg"),
        CheckConstraint("orders >= 0", name="kpi_rev_daily_orders_nonneg"),
        CheckConstraint("units >= 0", name="kpi_rev_daily_units_nonneg"),
        CheckConstraint(
            "channel IN ('ONLINE', 'STORE')",
            name="kpi_rev_daily_channel_check",
        ),
        Index("ix_kpi_rev_daily_date", "date_key"),
        Index("ix_kpi_rev_daily_state", "state_key"),
        Index("ix_kpi_rev_daily_channel", "channel"),
        Index("ix_kpi_rev_daily_category", "category_code"),
        {"schema": "kpis"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    date_key: Mapped[int] = mapped_column(
        ForeignKey("analytical.dim_date.date_key"), nullable=False
    )
    full_date: Mapped[date] = mapped_column(Date, nullable=False)
    state_key: Mapped[int] = mapped_column(
        ForeignKey("analytical.dim_state.state_key"), nullable=False
    )
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    category_code: Mapped[str] = mapped_column(String(20), nullable=False)

    revenue: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    orders: Mapped[int] = mapped_column(Integer, nullable=False)
    units: Mapped[int] = mapped_column(Integer, nullable=False)
    aov: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, comment="Average Order Value"
    )