"""Modelo STAGING para clientes.

Datos limpios y tipados de raw.customers.

Diferencias respecto a RAW:
- Enums como String + CHECK constraint.
- Sin metadata de ingesta.
- Columna derivada: age (calculado desde birth_date).
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Index,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class StagingCustomer(Base):
    """Cliente limpio y tipado."""

    __tablename__ = "customers"
    __table_args__ = (
        CheckConstraint(
            "gender IN ('MALE', 'FEMALE', 'OTHER')",
            name="stg_customers_gender_check",
        ),
        CheckConstraint(
            "profile IN ('NEW', 'ONE_TIME', 'OCCASIONAL', 'REGULAR', 'LOYAL', 'INACTIVE')",
            name="stg_customers_profile_check",
        ),
        CheckConstraint(
            "channel_preference IN ('ONLINE', 'STORE', 'OMNICHANNEL')",
            name="stg_customers_channel_check",
        ),
        CheckConstraint(
            "preferred_segment IN ('WOMEN', 'MEN', 'KIDS', 'UNISEX')",
            name="stg_customers_segment_check",
        ),
        CheckConstraint(
            "price_sensitivity IN ('LOW', 'MEDIUM', 'HIGH')",
            name="stg_customers_price_sens_check",
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="stg_customers_status_check",
        ),
        CheckConstraint(
            "total_orders >= 0",
            name="stg_customers_total_orders_nonnegative",
        ),
        CheckConstraint(
            "total_revenue >= 0",
            name="stg_customers_total_revenue_nonnegative",
        ),
        CheckConstraint(
            "total_units >= 0",
            name="stg_customers_total_units_nonnegative",
        ),
        Index("ix_stg_customers_state", "state_id"),
        Index("ix_stg_customers_profile", "profile"),
        Index("ix_stg_customers_channel", "channel_preference"),
        Index("ix_stg_customers_segment", "preferred_segment"),
        Index("ix_stg_customers_status", "status"),
        {"schema": "staging"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        comment="Mismo UUID del origen",
    )

    customer_code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    age: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Edad calculada al momento de la ingesta",
    )
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    state_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(10), nullable=False)
    profile: Mapped[str] = mapped_column(String(20), nullable=False)
    channel_preference: Mapped[str] = mapped_column(String(20), nullable=False)
    preferred_segment: Mapped[str] = mapped_column(String(20), nullable=False)
    price_sensitivity: Mapped[str] = mapped_column(String(20), nullable=False)
    signup_date: Mapped[date] = mapped_column(Date, nullable=False)
    first_order_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_order_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    total_orders: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    total_revenue: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default="0"
    )
    total_units: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="ACTIVE")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    staged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Cuándo se procesó a STAGING",
    )