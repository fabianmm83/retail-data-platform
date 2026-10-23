"""Transformadores RAW → STAGING.

Cada función:

1. Trunca la tabla STAGING destino.
2. Inserta desde RAW con transformaciones (SQL puro).
3. Es idempotente: correr dos veces deja el mismo estado.

Uso:

    from app.db.session import TargetSessionLocal
    from app.staging.transformers import transform_all

    with TargetSessionLocal() as db:
        results = transform_all(db)
"""

from __future__ import annotations

import logging
from datetime import date, datetime

from sqlalchemy import text
from sqlalchemy.orm import Session


logger = logging.getLogger(__name__)


# =============================================================================
# CUSTOMERS
# =============================================================================

TRANSFORM_CUSTOMERS_SQL = text(
    """
    INSERT INTO staging.customers (
        id,
        customer_code,
        first_name,
        last_name,
        email,
        phone,
        birth_date,
        age,
        gender,
        state_id,
        city,
        postal_code,
        profile,
        channel_preference,
        preferred_segment,
        price_sensitivity,
        signup_date,
        first_order_date,
        last_order_date,
        total_orders,
        total_revenue,
        total_units,
        status,
        created_at,
        updated_at
    )
    SELECT
        r.id,
        TRIM(r.customer_code),
        TRIM(r.first_name),
        TRIM(r.last_name),
        LOWER(TRIM(r.email)),
        TRIM(r.phone),
        r.birth_date,
        -- Age al día de hoy (o al start_date si tuviera sentido)
        DATE_PART('year', AGE(CURRENT_DATE, r.birth_date))::int AS age,
        r.gender,
        r.state_id,
        TRIM(r.city),
        TRIM(r.postal_code),
        r.profile,
        r.channel_preference,
        r.preferred_segment,
        r.price_sensitivity,
        r.signup_date,
        r.first_order_date,
        r.last_order_date,
        r.total_orders,
        r.total_revenue,
        r.total_units,
        r.status,
        r.created_at,
        r.updated_at
    FROM raw.customers r
    """
)


def transform_customers(db: Session) -> int:
    """Transforma raw.customers → staging.customers.

    Returns:
        Número de filas insertadas.
    """
    logger.info("→ staging.customers")
    db.execute(text("TRUNCATE TABLE staging.customers"))
    result = db.execute(TRANSFORM_CUSTOMERS_SQL)
    db.flush()
    rows = result.rowcount or 0
    logger.info("  %d filas", rows)
    return rows


# =============================================================================
# ORDERS
# =============================================================================

TRANSFORM_ORDERS_SQL = text(
    """
    INSERT INTO staging.orders (
        id,
        order_number,
        customer_id,
        state_id,
        location_id,
        channel,
        status,
        order_date,
        payment_method,
        paid,
        subtotal,
        discount,
        shipping_cost,
        total,
        line_count,
        created_at,
        updated_at
    )
    SELECT
        r.id,
        TRIM(r.order_number),
        r.customer_id,
        r.state_id,
        r.location_id,
        r.channel,
        r.status,
        r.order_date,
        r.payment_method,
        r.paid,
        r.subtotal,
        r.discount,
        r.shipping_cost,
        r.total,
        -- line_count: número de items de la orden (derivado)
        COALESCE(
            (SELECT COUNT(*) FROM raw.order_items oi WHERE oi.order_id = r.id),
            0
        )::int AS line_count,
        r.created_at,
        r.updated_at
    FROM raw.orders r
    """
)


def transform_orders(db: Session) -> int:
    """Transforma raw.orders → staging.orders."""
    logger.info("→ staging.orders")
    db.execute(text("TRUNCATE TABLE staging.orders"))
    result = db.execute(TRANSFORM_ORDERS_SQL)
    db.flush()
    rows = result.rowcount or 0
    logger.info("  %d filas", rows)
    return rows


# =============================================================================
# ORDER_ITEMS
# =============================================================================

TRANSFORM_ORDER_ITEMS_SQL = text(
    """
    INSERT INTO staging.order_items (
        id,
        order_id,
        variant_id,
        quantity,
        unit_price,
        discount,
        subtotal,
        created_at,
        updated_at
    )
    SELECT
        r.id,
        r.order_id,
        r.variant_id,
        r.quantity,
        r.unit_price,
        r.discount,
        r.subtotal,
        r.created_at,
        r.updated_at
    FROM raw.order_items r
    """
)


def transform_order_items(db: Session) -> int:
    """Transforma raw.order_items → staging.order_items."""
    logger.info("→ staging.order_items")
    db.execute(text("TRUNCATE TABLE staging.order_items"))
    result = db.execute(TRANSFORM_ORDER_ITEMS_SQL)
    db.flush()
    rows = result.rowcount or 0
    logger.info("  %d filas", rows)
    return rows


# =============================================================================
# ORQUESTADOR
# =============================================================================

TRANSFORMERS = {
    "customers": transform_customers,
    "orders": transform_orders,
    "order_items": transform_order_items,
}


def transform_all(db: Session, entities: list[str] | None = None) -> dict[str, int]:
    """Transforma todas las entidades (o las especificadas).

    Args:
        db: sesión al data platform.
        entities: lista de entidades a transformar (None = todas).

    Returns:
        Dict {entity_name: rows_inserted}.
    """
    if entities is None:
        entities = list(TRANSFORMERS.keys())

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