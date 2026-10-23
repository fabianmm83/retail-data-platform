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
    logger.info("→ staging.order_items")
    db.execute(text("TRUNCATE TABLE staging.order_items"))
    result = db.execute(TRANSFORM_ORDER_ITEMS_SQL)
    db.flush()
    rows = result.rowcount or 0
    logger.info("  %d filas", rows)
    return rows


# =============================================================================
# STATES
# =============================================================================

TRANSFORM_STATES_SQL = text(
    """
    INSERT INTO staging.states (
        id,
        code,
        name,
        region,
        income_group,
        population_share,
        income_index,
        online_penetration,
        regional_factor,
        growth_rate,
        status,
        created_at,
        updated_at
    )
    SELECT
        r.id,
        UPPER(TRIM(r.code)),
        TRIM(r.name),
        r.region,
        r.income_group,
        r.population_share,
        r.income_index,
        r.online_penetration,
        r.regional_factor,
        r.growth_rate,
        r.status,
        r.created_at,
        r.updated_at
    FROM raw.states r
    """
)


def transform_states(db: Session) -> int:
    logger.info("→ staging.states")
    db.execute(text("TRUNCATE TABLE staging.states"))
    result = db.execute(TRANSFORM_STATES_SQL)
    db.flush()
    rows = result.rowcount or 0
    logger.info("  %d filas", rows)
    return rows


# =============================================================================
# CATEGORIES
# =============================================================================

TRANSFORM_CATEGORIES_SQL = text(
    """
    INSERT INTO staging.categories (
        id,
        code,
        name,
        department,
        seasonality,
        status,
        created_at,
        updated_at
    )
    SELECT
        r.id,
        UPPER(TRIM(r.code)),
        TRIM(r.name),
        r.department,
        r.seasonality,
        r.status,
        r.created_at,
        r.updated_at
    FROM raw.categories r
    """
)


def transform_categories(db: Session) -> int:
    logger.info("→ staging.categories")
    db.execute(text("TRUNCATE TABLE staging.categories"))
    result = db.execute(TRANSFORM_CATEGORIES_SQL)
    db.flush()
    rows = result.rowcount or 0
    logger.info("  %d filas", rows)
    return rows


# =============================================================================
# LOCATIONS
# =============================================================================

TRANSFORM_LOCATIONS_SQL = text(
    """
    INSERT INTO staging.locations (
        id,
        code,
        name,
        location_type,
        state_id,
        capacity_units,
        status,
        created_at,
        updated_at
    )
    SELECT
        r.id,
        UPPER(TRIM(r.code)),
        TRIM(r.name),
        r.location_type,
        r.state_id,
        r.capacity_units,
        r.status,
        r.created_at,
        r.updated_at
    FROM raw.locations r
    """
)


def transform_locations(db: Session) -> int:
    logger.info("→ staging.locations")
    db.execute(text("TRUNCATE TABLE staging.locations"))
    result = db.execute(TRANSFORM_LOCATIONS_SQL)
    db.flush()
    rows = result.rowcount or 0
    logger.info("  %d filas", rows)
    return rows


# =============================================================================
# PRODUCTS
# =============================================================================

TRANSFORM_PRODUCTS_SQL = text(
    """
    INSERT INTO staging.products (
        id,
        style_code,
        name,
        segment,
        age_group,
        category_id,
        sport,
        branded,
        base_price,
        base_cost,
        demand_profile,
        lifecycle_stage,
        launch_date,
        status,
        created_at,
        updated_at
    )
    SELECT
        r.id,
        UPPER(TRIM(r.style_code)),
        TRIM(r.name),
        r.segment,
        r.age_group,
        r.category_id,
        r.sport,
        r.branded,
        r.base_price,
        r.base_cost,
        r.demand_profile,
        r.lifecycle_stage,
        r.launch_date,
        r.status,
        r.created_at,
        r.updated_at
    FROM raw.products r
    """
)


def transform_products(db: Session) -> int:
    logger.info("→ staging.products")
    db.execute(text("TRUNCATE TABLE staging.products"))
    result = db.execute(TRANSFORM_PRODUCTS_SQL)
    db.flush()
    rows = result.rowcount or 0
    logger.info("  %d filas", rows)
    return rows


# =============================================================================
# PRODUCT VARIANTS
# =============================================================================

TRANSFORM_PRODUCT_VARIANTS_SQL = text(
    """
    INSERT INTO staging.product_variants (
        id,
        sku,
        product_id,
        size,
        color,
        barcode,
        status,
        created_at,
        updated_at
    )
    SELECT
        r.id,
        UPPER(TRIM(r.sku)),
        r.product_id,
        TRIM(r.size),
        r.color,
        TRIM(r.barcode),
        r.status,
        r.created_at,
        r.updated_at
    FROM raw.product_variants r
    """
)


def transform_product_variants(db: Session) -> int:
    logger.info("→ staging.product_variants")
    db.execute(text("TRUNCATE TABLE staging.product_variants"))
    result = db.execute(TRANSFORM_PRODUCT_VARIANTS_SQL)
    db.flush()
    rows = result.rowcount or 0
    logger.info("  %d filas", rows)
    return rows


# =============================================================================
# ORQUESTADOR
# =============================================================================

TRANSFORMERS = {
    "states": transform_states,
    "categories": transform_categories,
    "locations": transform_locations,
    "products": transform_products,
    "product_variants": transform_product_variants,
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