"""Dimensión cliente."""

import uuid
from datetime import date

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DimCustomer(Base):
    """Clientes con surrogate key."""

    __tablename__ = "dim_customer"
    __table_args__ = (
        CheckConstraint(
            "profile IN ('NEW', 'ONE_TIME', 'OCCASIONAL', 'REGULAR', 'LOYAL', 'INACTIVE')",
            name="dim_customer_profile_check",
        ),
        CheckConstraint(
            "channel_preference IN ('ONLINE', 'STORE', 'OMNICHANNEL')",
            name="dim_customer_channel_check",
        ),
        CheckConstraint(
            "preferred_segment IN ('WOMEN', 'MEN', 'KIDS', 'UNISEX')",
            name="dim_customer_segment_check",
        ),
        CheckConstraint(
            "price_sensitivity IN ('LOW', 'MEDIUM', 'HIGH')",
            name="dim_customer_price_sens_check",
        ),
        Index("ix_dim_customer_profile", "profile"),
        Index("ix_dim_customer_channel", "channel_preference"),
        Index("ix_dim_customer_segment", "preferred_segment"),
        Index("ix_dim_customer_state", "state_key"),
        {"schema": "analytical"},
    )

    customer_key: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, unique=True
    )
    customer_code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    age_group: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="<25, 25-34, 35-44, 45-54, 55+",
    )
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    profile: Mapped[str] = mapped_column(String(20), nullable=False)
    channel_preference: Mapped[str] = mapped_column(String(20), nullable=False)
    preferred_segment: Mapped[str] = mapped_column(String(20), nullable=False)
    price_sensitivity: Mapped[str] = mapped_column(String(20), nullable=False)
    state_key: Mapped[int] = mapped_column(
        ForeignKey("analytical.dim_state.state_key"), nullable=False
    )
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(10), nullable=False)
    signup_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)