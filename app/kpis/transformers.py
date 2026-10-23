"""Transformadores ANALYTICAL → KPIS.

Cada función:

1. Trunca la tabla KPI destino.
2. Inserta agregando desde analytical.fact_sales + dims.
3. Es idempotente.
"""

from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.orm import Session


logger = logging.getLogger(__name__)


# =============================================================================
# REVENUE_DAILY
# =============================================================================

TRANSFORM_REVENUE_DAILY_SQL = text(
    """
    INSERT INTO kpis.revenue_daily (
        date_key,
        full_date,
        state_key,
        channel,
        category_code,
        revenue,
        orders,
        units,
        aov
    )
    SELECT
        fs.date_key,
        dd.full_date,
        fs.state_key,
        fs.channel,
        dp.category_code,
        SUM(fs.subtotal)::numeric(14,2) AS revenue,
        COUNT(DISTINCT fs.order_id)::int AS orders,
        SUM(fs.quantity)::int AS units,
        (SUM(fs.subtotal) / NULLIF(COUNT(DISTINCT fs.order_id), 0))::numeric(12,2) AS aov
    FROM analytical.fact_sales fs
    INNER JOIN analytical.dim_date dd ON dd.date_key = fs.date_key
    INNER JOIN analytical.dim_product dp ON dp.product_key = fs.product_key
    GROUP BY fs.date_key, dd.full_date, fs.state_key, fs.channel, dp.category_code
    ORDER BY fs.date_key, fs.state_key, fs.channel, dp.category_code
    """
)


def transform_revenue_daily(db: Session) -> int:
    logger.info("→ kpis.revenue_daily")
    db.execute(text("TRUNCATE TABLE kpis.revenue_daily"))
    result = db.execute(TRANSFORM_REVENUE_DAILY_SQL)
    db.flush()
    rows = result.rowcount or 0
    logger.info("  %d filas", rows)
    return rows


# =============================================================================
# REVENUE_BY_PRODUCT
# =============================================================================

TRANSFORM_REVENUE_BY_PRODUCT_SQL = text(
    """
    INSERT INTO kpis.revenue_by_product (
        product_key,
        style_code,
        product_name,
        year,
        month,
        revenue,
        units,
        orders,
        avg_price
    )
    SELECT
        fs.product_key,
        dp.style_code,
        dp.name,
        dd.year,
        dd.month,
        SUM(fs.subtotal)::numeric(14,2) AS revenue,
        SUM(fs.quantity)::int AS units,
        COUNT(DISTINCT fs.order_id)::int AS orders,
        AVG(fs.unit_price)::numeric(10,2) AS avg_price
    FROM analytical.fact_sales fs
    INNER JOIN analytical.dim_date dd ON dd.date_key = fs.date_key
    INNER JOIN analytical.dim_product dp ON dp.product_key = fs.product_key
    GROUP BY fs.product_key, dp.style_code, dp.name, dd.year, dd.month
    ORDER BY dd.year, dd.month, revenue DESC
    """
)


def transform_revenue_by_product(db: Session) -> int:
    logger.info("→ kpis.revenue_by_product")
    db.execute(text("TRUNCATE TABLE kpis.revenue_by_product"))
    result = db.execute(TRANSFORM_REVENUE_BY_PRODUCT_SQL)
    db.flush()
    rows = result.rowcount or 0
    logger.info("  %d filas", rows)
    return rows


# =============================================================================
# REVENUE_BY_STATE
# =============================================================================

TRANSFORM_REVENUE_BY_STATE_SQL = text(
    """
    INSERT INTO kpis.revenue_by_state (
        state_key,
        state_code,
        state_name,
        year,
        month,
        revenue,
        units,
        orders,
        aov
    )
    SELECT
        fs.state_key,
        ds.code,
        ds.name,
        dd.year,
        dd.month,
        SUM(fs.subtotal)::numeric(14,2) AS revenue,
        SUM(fs.quantity)::int AS units,
        COUNT(DISTINCT fs.order_id)::int AS orders,
        (SUM(fs.subtotal) / NULLIF(COUNT(DISTINCT fs.order_id), 0))::numeric(12,2) AS aov
    FROM analytical.fact_sales fs
    INNER JOIN analytical.dim_date dd ON dd.date_key = fs.date_key
    INNER JOIN analytical.dim_state ds ON ds.state_key = fs.state_key
    GROUP BY fs.state_key, ds.code, ds.name, dd.year, dd.month
    ORDER BY dd.year, dd.month, revenue DESC
    """
)


def transform_revenue_by_state(db: Session) -> int:
    logger.info("→ kpis.revenue_by_state")
    db.execute(text("TRUNCATE TABLE kpis.revenue_by_state"))
    result = db.execute(TRANSFORM_REVENUE_BY_STATE_SQL)
    db.flush()
    rows = result.rowcount or 0
    logger.info("  %d filas", rows)
    return rows


# =============================================================================
# REVENUE_BY_CHANNEL
# =============================================================================

TRANSFORM_REVENUE_BY_CHANNEL_SQL = text(
    """
    INSERT INTO kpis.revenue_by_channel (
        channel,
        year,
        month,
        revenue,
        units,
        orders,
        aov
    )
    SELECT
        fs.channel,
        dd.year,
        dd.month,
        SUM(fs.subtotal)::numeric(14,2) AS revenue,
        SUM(fs.quantity)::int AS units,
        COUNT(DISTINCT fs.order_id)::int AS orders,
        (SUM(fs.subtotal) / NULLIF(COUNT(DISTINCT fs.order_id), 0))::numeric(12,2) AS aov
    FROM analytical.fact_sales fs
    INNER JOIN analytical.dim_date dd ON dd.date_key = fs.date_key
    GROUP BY fs.channel, dd.year, dd.month
    ORDER BY dd.year, dd.month, fs.channel
    """
)


def transform_revenue_by_channel(db: Session) -> int:
    logger.info("→ kpis.revenue_by_channel")
    db.execute(text("TRUNCATE TABLE kpis.revenue_by_channel"))
    result = db.execute(TRANSFORM_REVENUE_BY_CHANNEL_SQL)
    db.flush()
    rows = result.rowcount or 0
    logger.info("  %d filas", rows)
    return rows


# =============================================================================
# ORQUESTADOR
# =============================================================================

TRANSFORMERS = {
    "revenue_daily": transform_revenue_daily,
    "revenue_by_product": transform_revenue_by_product,
    "revenue_by_state": transform_revenue_by_state,
    "revenue_by_channel": transform_revenue_by_channel,
}

TRANSFORM_ORDER = [
    "revenue_daily",
    "revenue_by_product",
    "revenue_by_state",
    "revenue_by_channel",
]


def transform_all(db: Session, entities: list[str] | None = None) -> dict[str, int]:
    if entities is None:
        entities = list(TRANSFORM_ORDER)
    else:
        entities = [e for e in TRANSFORM_ORDER if e in entities]

    results: dict[str, int] = {}

    for entity in entities:
        if entity not in TRANSFORMERS:
            raise ValueError(
                f"Entidad desconocida: {entity}. "
                f"Válidas: {list(TRANSFORMERS.keys())}"
            )
        transformer = TRANSFORMERS[entity]
        rows = transformer(db)
        results[entity] = rows

    return results