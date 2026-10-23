"""Endpoints de KPIs."""

from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.kpis.revenue_by_channel import KpiRevenueByChannel
from app.kpis.revenue_by_product import KpiRevenueByProduct
from app.kpis.revenue_by_state import KpiRevenueByState
from app.kpis.revenue_daily import KpiRevenueDaily
from app.kpis.logistics_performance import KpiLogisticsPerformance
from app.schemas.kpis import (
    OverviewKPI,
    RevenueByCategoryRead,
    RevenueByChannelAggregated,
     LogisticsPerformanceRead,
    RevenueByChannelRead,
    RevenueByProductRead,
    RevenueByStateAggregated,
    RevenueByStateRead,
    RevenueDailyRead,
    RevenueDailySeriesPoint,
)


router = APIRouter(prefix="/kpis", tags=["kpis"])


# =============================================================================
# OVERVIEW
# =============================================================================


@router.get("/overview", response_model=OverviewKPI)
def get_overview(db: Session = Depends(get_db)) -> OverviewKPI:
    """Snapshot general del negocio."""

    # Totales
    total = db.execute(
        select(
            func.coalesce(func.sum(KpiRevenueDaily.revenue), 0),
            func.coalesce(func.sum(KpiRevenueDaily.orders), 0),
            func.coalesce(func.sum(KpiRevenueDaily.units), 0),
        )
    ).one()
    total_revenue = Decimal(str(total[0]))
    total_orders = int(total[1])
    total_units = int(total[2])
    aov = (total_revenue / total_orders).quantize(Decimal("0.01")) if total_orders > 0 else Decimal("0")

    # Por canal
    channel_rows = db.execute(
        select(
            KpiRevenueDaily.channel,
            func.sum(KpiRevenueDaily.revenue),
        ).group_by(KpiRevenueDaily.channel)
    ).all()
    channel_map = {r[0]: Decimal(str(r[1])) for r in channel_rows}
    online = channel_map.get("ONLINE", Decimal("0"))
    store = channel_map.get("STORE", Decimal("0"))
    online_share = (online / total_revenue).quantize(Decimal("0.0001")) if total_revenue > 0 else Decimal("0")

    # Top estado
    top_state_row = db.execute(
        select(
            KpiRevenueByState.state_name,
            func.sum(KpiRevenueByState.revenue).label("rev"),
        ).group_by(KpiRevenueByState.state_name)
        .order_by(func.sum(KpiRevenueByState.revenue).desc())
        .limit(1)
    ).first()
    top_state = top_state_row[0] if top_state_row else "N/A"

    # Top categoría
    top_cat_row = db.execute(
        select(
            KpiRevenueDaily.category_code,
            func.sum(KpiRevenueDaily.revenue).label("rev"),
        ).group_by(KpiRevenueDaily.category_code)
        .order_by(func.sum(KpiRevenueDaily.revenue).desc())
        .limit(1)
    ).first()
    top_category = top_cat_row[0] if top_cat_row else "N/A"

    return OverviewKPI(
        total_revenue=total_revenue,
        total_orders=total_orders,
        total_units=total_units,
        aov=aov,
        online_revenue=online,
        store_revenue=store,
        online_share=online_share,
        top_state=top_state,
        top_category=top_category,
    )


# =============================================================================
# REVENUE DAILY
# =============================================================================


@router.get("/revenue/daily", response_model=list[RevenueDailySeriesPoint])
def get_revenue_daily(
    db: Session = Depends(get_db),
) -> list[RevenueDailySeriesPoint]:
    """Serie temporal de revenue agregada por día (todos los canales/estados)."""

    rows = db.execute(
        select(
            KpiRevenueDaily.full_date,
            func.sum(KpiRevenueDaily.revenue).label("revenue"),
            func.sum(KpiRevenueDaily.orders).label("orders"),
            func.sum(KpiRevenueDaily.units).label("units"),
        )
        .group_by(KpiRevenueDaily.full_date)
        .order_by(KpiRevenueDaily.full_date)
    ).all()

    return [
        RevenueDailySeriesPoint(
            date=r[0],
            revenue=Decimal(str(r[1])),
            orders=int(r[2]),
            units=int(r[3]),
        )
        for r in rows
    ]


@router.get("/revenue/daily/raw", response_model=list[RevenueDailyRead])
def get_revenue_daily_raw(
    db: Session = Depends(get_db),
    limit: int = Query(default=500, ge=1, le=5000),
    offset: int = Query(default=0, ge=0),
) -> list[KpiRevenueDaily]:
    """Datos crudos de revenue_daily (día × estado × canal × categoría)."""

    stmt = (
        select(KpiRevenueDaily)
        .order_by(KpiRevenueDaily.date_key, KpiRevenueDaily.state_key)
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(stmt).all())


# =============================================================================
# REVENUE BY PRODUCT
# =============================================================================


@router.get("/revenue/products", response_model=list[RevenueByProductRead])
def get_revenue_by_product(
    db: Session = Depends(get_db),
    limit: int = Query(default=32, ge=1, le=100),
) -> list[KpiRevenueByProduct]:
    """Top productos por revenue."""

    stmt = (
        select(KpiRevenueByProduct)
        .order_by(KpiRevenueByProduct.revenue.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


# =============================================================================
# REVENUE BY STATE
# =============================================================================


@router.get("/revenue/states", response_model=list[RevenueByStateAggregated])
def get_revenue_by_state(
    db: Session = Depends(get_db),
) -> list[RevenueByStateAggregated]:
    """Revenue agregado por estado (sin dimensión temporal)."""

    rows = db.execute(
        select(
            KpiRevenueByState.state_code,
            KpiRevenueByState.state_name,
            func.sum(KpiRevenueByState.revenue).label("revenue"),
            func.sum(KpiRevenueByState.units).label("units"),
            func.sum(KpiRevenueByState.orders).label("orders"),
        )
        .group_by(KpiRevenueByState.state_code, KpiRevenueByState.state_name)
        .order_by(func.sum(KpiRevenueByState.revenue).desc())
    ).all()

    result = []
    for r in rows:
        revenue = Decimal(str(r[2]))
        orders = int(r[4])
        aov = (revenue / orders).quantize(Decimal("0.01")) if orders > 0 else Decimal("0")
        result.append(
            RevenueByStateAggregated(
                state_code=r[0],
                state_name=r[1],
                revenue=revenue,
                units=int(r[3]),
                orders=orders,
                aov=aov,
            )
        )
    return result


@router.get("/revenue/states/raw", response_model=list[RevenueByStateRead])
def get_revenue_by_state_raw(
    db: Session = Depends(get_db),
    limit: int = Query(default=500, ge=1, le=5000),
) -> list[KpiRevenueByState]:
    """Datos crudos de revenue_by_state."""

    stmt = (
        select(KpiRevenueByState)
        .order_by(KpiRevenueByState.revenue.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


# =============================================================================
# REVENUE BY CHANNEL
# =============================================================================


@router.get("/revenue/channels", response_model=list[RevenueByChannelAggregated])
def get_revenue_by_channel(
    db: Session = Depends(get_db),
) -> list[RevenueByChannelAggregated]:
    """Revenue agregado por canal (sin dimensión temporal)."""

    rows = db.execute(
        select(
            KpiRevenueByChannel.channel,
            func.sum(KpiRevenueByChannel.revenue).label("revenue"),
            func.sum(KpiRevenueByChannel.units).label("units"),
            func.sum(KpiRevenueByChannel.orders).label("orders"),
        )
        .group_by(KpiRevenueByChannel.channel)
        .order_by(func.sum(KpiRevenueByChannel.revenue).desc())
    ).all()

    result = []
    for r in rows:
        revenue = Decimal(str(r[1]))
        orders = int(r[3])
        aov = (revenue / orders).quantize(Decimal("0.01")) if orders > 0 else Decimal("0")
        result.append(
            RevenueByChannelAggregated(
                channel=r[0],
                revenue=revenue,
                units=int(r[2]),
                orders=orders,
                aov=aov,
            )
        )
    return result


# =============================================================================
# REVENUE BY CATEGORY
# =============================================================================


@router.get("/revenue/categories", response_model=list[RevenueByCategoryRead])
def get_revenue_by_category(
    db: Session = Depends(get_db),
) -> list[RevenueByCategoryRead]:
    """Revenue agregado por categoría (sin dimensión temporal)."""

    rows = db.execute(
        select(
            KpiRevenueDaily.category_code,
            func.sum(KpiRevenueDaily.revenue).label("revenue"),
            func.sum(KpiRevenueDaily.units).label("units"),
            func.sum(KpiRevenueDaily.orders).label("orders"),
        )
        .group_by(KpiRevenueDaily.category_code)
        .order_by(func.sum(KpiRevenueDaily.revenue).desc())
    ).all()

    result = []
    for r in rows:
        revenue = Decimal(str(r[1]))
        orders = int(r[3])
        aov = (revenue / orders).quantize(Decimal("0.01")) if orders > 0 else Decimal("0")
        result.append(
            RevenueByCategoryRead(
                category_code=r[0],
                revenue=revenue,
                units=int(r[2]),
                orders=orders,
                aov=aov,
            )
        )
    return result



# =============================================================================
# LOGISTICS
# =============================================================================


@router.get("/logistics", response_model=list[LogisticsPerformanceRead])
def get_logistics_performance(
    db: Session = Depends(get_db),
) -> list[KpiLogisticsPerformance]:
    """Performance logística por mes."""
    stmt = select(KpiLogisticsPerformance).order_by(
        KpiLogisticsPerformance.year,
        KpiLogisticsPerformance.month,
    )
    return list(db.scalars(stmt).all())