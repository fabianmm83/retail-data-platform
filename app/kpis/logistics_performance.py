"""KPI: performance logística por carrier × mes."""

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


class KpiLogisticsPerformance(Base):
    """Performance de envíos agrupada por carrier × mes."""

    __tablename__ = "logistics_performance"
    __table_args__ = (
        CheckConstraint(
            "shipments >= 0",
            name="kpi_logistics_shipments_nonneg",
        ),
        CheckConstraint(
            "on_time_rate >= 0 AND on_time_rate <= 1",
            name="kpi_logistics_on_time_rate_range",
        ),
        CheckConstraint(
            "avg_shipping_cost >= 0",
            name="kpi_logistics_avg_cost_nonneg",
        ),
        Index("ix_kpi_logistics_year_month", "year", "month"),
        {"schema": "kpis"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)

    shipments: Mapped[int] = mapped_column(Integer, nullable=False)
    delivered: Mapped[int] = mapped_column(Integer, nullable=False)
    delayed: Mapped[int] = mapped_column(Integer, nullable=False)
    in_transit: Mapped[int] = mapped_column(Integer, nullable=False)

    on_time_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 4), nullable=False, comment="delivered on time / delivered"
    )
    avg_lead_time_days: Mapped[Decimal] = mapped_column(
        Numeric(6, 2), nullable=False, comment="Promedio de días delivered - shipped"
    )
    avg_shipping_cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    total_shipping_cost: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False
    )