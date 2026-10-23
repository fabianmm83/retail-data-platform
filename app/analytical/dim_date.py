"""Dimensión fecha (calendario)."""

from datetime import date

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DimDate(Base):
    """Calendario generado 2020–2030."""

    __tablename__ = "dim_date"
    __table_args__ = (
        CheckConstraint("year >= 2020 AND year <= 2030", name="dim_date_year_range"),
        CheckConstraint("month >= 1 AND month <= 12", name="dim_date_month_range"),
        CheckConstraint("quarter >= 1 AND quarter <= 4", name="dim_date_quarter_range"),
        Index("ix_dim_date_full_date", "full_date"),
        Index("ix_dim_date_year_month", "year", "month"),
        {"schema": "analytical"},
    )

    date_key: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment="YYYYMMDD",
    )
    full_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    quarter: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    month_name: Mapped[str] = mapped_column(String(20), nullable=False)
    week_of_year: Mapped[int] = mapped_column(Integer, nullable=False)
    day_of_month: Mapped[int] = mapped_column(Integer, nullable=False)
    day_of_week: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="ISO: 1=lunes, 7=domingo"
    )
    day_name: Mapped[str] = mapped_column(String(20), nullable=False)
    is_weekend: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_holiday: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )