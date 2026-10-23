"""KPI: revenue por canal × mes."""

from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class KpiRevenueByChannel(Base):
    """Revenue agregado por canal × mes."""

    __tablename__ = "revenue_by_channel"
    __table_args__ = (
        CheckConstraint("revenue >= 0", name="kpi_rev_chan_revenue_nonneg"),
        CheckConstraint("units >= 0", name="kpi_rev_chan_units_nonneg"),
        CheckConstraint("orders >= 0", name="kpi_rev_chan_orders_nonneg"),
        CheckConstraint(
            "channel IN ('ONLINE', 'STORE')",
            name="kpi_rev_chan_channel_check",
        ),
        Index("ix_kpi_rev_chan_channel", "channel"),
        Index("ix_kpi_rev_chan_year_month", "year", "month"),
        {"schema": "kpis"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)

    revenue: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    units: Mapped[int] = mapped_column(Integer, nullable=False)
    orders: Mapped[int] = mapped_column(Integer, nullable=False)
    aov: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)