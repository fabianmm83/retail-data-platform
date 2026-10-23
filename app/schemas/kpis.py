"""Schemas Pydantic para KPIs."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


# =============================================================================
# HEALTH
# =============================================================================


class HealthResponse(BaseModel):
    status: str
    service: str
    database: str


# =============================================================================
# OVERVIEW
# =============================================================================


class OverviewKPI(BaseModel):
    """Snapshot general del negocio."""

    total_revenue: Decimal
    total_orders: int
    total_units: int
    aov: Decimal
    online_revenue: Decimal
    store_revenue: Decimal
    online_share: Decimal
    top_state: str
    top_category: str


# =============================================================================
# REVENUE DAILY
# =============================================================================


class RevenueDailyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date_key: int
    full_date: date
    state_key: int
    channel: str
    category_code: str
    revenue: Decimal
    orders: int
    units: int
    aov: Decimal


class RevenueDailySeriesPoint(BaseModel):
    """Punto de serie temporal para gráficos."""

    date: date
    revenue: Decimal
    orders: int
    units: int


# =============================================================================
# REVENUE BY PRODUCT
# =============================================================================


class RevenueByProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_key: int
    style_code: str
    product_name: str
    year: int
    month: int
    revenue: Decimal
    units: int
    orders: int
    avg_price: Decimal


# =============================================================================
# REVENUE BY STATE
# =============================================================================


class RevenueByStateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    state_key: int
    state_code: str
    state_name: str
    year: int
    month: int
    revenue: Decimal
    units: int
    orders: int
    aov: Decimal


class RevenueByStateAggregated(BaseModel):
    """Estado agregado sin dimensión temporal."""

    state_code: str
    state_name: str
    revenue: Decimal
    units: int
    orders: int
    aov: Decimal


# =============================================================================
# REVENUE BY CHANNEL
# =============================================================================


class RevenueByChannelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    channel: str
    year: int
    month: int
    revenue: Decimal
    units: int
    orders: int
    aov: Decimal


class RevenueByChannelAggregated(BaseModel):
    """Canal agregado sin dimensión temporal."""

    channel: str
    revenue: Decimal
    units: int
    orders: int
    aov: Decimal


# =============================================================================
# REVENUE BY CATEGORY
# =============================================================================


class RevenueByCategoryRead(BaseModel):
    """Categoría agregada sin dimensión temporal."""

    category_code: str
    revenue: Decimal
    units: int
    orders: int
    aov: Decimal