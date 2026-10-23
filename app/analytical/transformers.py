"""Transformadores STAGING → ANALYTICAL.

Cada función:

1. Trunca la tabla ANALYTICAL destino.
2. Inserta desde STAGING con transformaciones (SQL puro).
3. Asigna surrogate keys deterministas con ROW_NUMBER().
4. Es idempotente: correr dos veces deja el mismo estado.

ORDEN IMPORTANTE: cargar dims antes que facts, y respetar
dependencias entre dims (state antes que customer/warehouse,
product antes que variant).
"""

from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.orm import Session


logger = logging.getLogger(__name__)


# =============================================================================
# DIM_DATE
# =============================================================================

TRANSFORM_DIM_DATE_SQL = text(
    """
    INSERT INTO analytical.dim_date (
        date_key,
        full_date,
        year,
        quarter,
        month,
        month_name,
        week_of_year,
        day_of_month,
        day_of_week,
        day_name,
        is_weekend,
        is_holiday
    )
    SELECT
        TO_CHAR(d, 'YYYYMMDD')::int AS date_key,
        d::date AS full_date,
        EXTRACT(YEAR FROM d)::int AS year,
        EXTRACT(QUARTER FROM d)::int AS quarter,
        EXTRACT(MONTH FROM d)::int AS month,
        TO_CHAR(d, 'TMMonth') AS month_name,
        EXTRACT(WEEK FROM d)::int AS week_of_year,
        EXTRACT(DAY FROM d)::int AS day_of_month,
        EXTRACT(ISODOW FROM d)::int AS day_of_week,
        TO_CHAR(d, 'TMDay') AS day_name,
        CASE WHEN EXTRACT(ISODOW FROM d) IN (6, 7) THEN TRUE ELSE FALSE END AS is_weekend,
        FALSE AS is_holiday
    FROM generate_series(
        '2020-01-01'::date,
        '2030-12-31'::date,
        '1 day'::interval
    ) AS d
    """
)


def transform_dim_date(db: Session) -> int:
    """Genera el calendario 2020–2030."""
    logger.info("→ analytical.dim_date")
    db.execute(text("TRUNCATE TABLE analytical.dim_date CASCADE"))
    result = db.execute(TRANSFORM_DIM_DATE_SQL)
    db.flush()
    rows = result.rowcount or 0
    logger.info("  %d filas", rows)
    return rows


# =============================================================================
# DIM_STATE
# =============================================================================

TRANSFORM_DIM_STATE_SQL = text(
    """
    INSERT INTO analytical.dim_state (
        state_key,
        state_id,
        code,
        name,
        region,
        income_group,
        population_share,
        online_penetration
    )
    SELECT
        ROW_NUMBER() OVER (ORDER BY s.code)::int AS state_key,
        s.id AS state_id,
        s.code,
        s.name,
        s.region,
        s.income_group,
        s.population_share,
        s.online_penetration
    FROM staging.states s
    """
)


def transform_dim_state(db: Session) -> int:
    """Carga los 10 estados."""
    logger.info("→ analytical.dim_state")
    db.execute(text("TRUNCATE TABLE analytical.dim_state CASCADE"))
    result = db.execute(TRANSFORM_DIM_STATE_SQL)
    db.flush()
    rows = result.rowcount or 0
    logger.info("  %d filas", rows)
    return rows


# =============================================================================
# DIM_PRODUCT
# =============================================================================

TRANSFORM_DIM_PRODUCT_SQL = text(
    """
    INSERT INTO analytical.dim_product (
        product_key,
        product_id,
        style_code,
        name,
        segment,
        age_group,
        category_code,
        category_name,
        sport,
        branded,
        base_price,
        base_cost,
        demand_profile,
        lifecycle_stage,
        launch_date
    )
    SELECT
        ROW_NUMBER() OVER (ORDER BY p.style_code)::int AS product_key,
        p.id AS product_id,
        p.style_code,
        p.name,
        p.segment,
        p.age_group,
        c.code AS category_code,
        c.name AS category_name,
        p.sport,
        p.branded,
        p.base_price,
        p.base_cost,
        p.demand_profile,
        p.lifecycle_stage,
        p.launch_date
    FROM staging.products p
    INNER JOIN staging.categories c ON c.id = p.category_id
    """
)







def transform_dim_product(db: Session) -> int:
    """Carga los 32 productos con su categoría. Requiere staging.categories."""
    logger.info("→ analytical.dim_product")
    db.execute(text("TRUNCATE TABLE analytical.dim_product CASCADE"))
    result = db.execute(TRANSFORM_DIM_PRODUCT_SQL)
    db.flush()
    rows = result.rowcount or 0
    logger.info("  %d filas", rows)
    return rows


# =============================================================================
# FACT_SHIPMENTS
# =============================================================================

TRANSFORM_FACT_SHIPMENTS_SQL = text(
    """
    INSERT INTO analytical.fact_shipments (
        date_key,
        warehouse_key,
        shipment_id,
        shipment_number,
        tracking_number,
        order_id,
        status,
        shipped_at,
        estimated_delivery,
        delivered_at,
        lead_time_days,
        is_on_time,
        shipping_cost,
        weight_kg
    )
    SELECT
        COALESCE(
            TO_CHAR(s.shipped_at, 'YYYYMMDD')::int,
            TO_CHAR(s.created_at, 'YYYYMMDD')::int
        ) AS date_key,
        dw.warehouse_key,
        s.id AS shipment_id,
        s.shipment_number,
        s.tracking_number,
        s.order_id,
        s.status,
        s.shipped_at,
        s.estimated_delivery,
        s.delivered_at,
        CASE
            WHEN s.delivered_at IS NOT NULL AND s.shipped_at IS NOT NULL
                THEN (s.delivered_at - s.shipped_at)
            ELSE NULL
        END AS lead_time_days,
        CASE
            WHEN s.delivered_at IS NOT NULL AND s.estimated_delivery IS NOT NULL
                THEN s.delivered_at <= s.estimated_delivery
            ELSE NULL
        END AS is_on_time,
        s.shipping_cost,
        s.weight_kg
    FROM staging.shipments s
    INNER JOIN analytical.dim_warehouse dw
        ON dw.location_id = s.origin_location_id
    """
)


def transform_fact_shipments(db: Session) -> int:
    """Carga el hecho de shipments. Requiere dim_date y dim_warehouse."""
    logger.info("→ analytical.fact_shipments")
    db.execute(text("TRUNCATE TABLE analytical.fact_shipments CASCADE"))
    result = db.execute(TRANSFORM_FACT_SHIPMENTS_SQL)
    db.flush()
    rows = result.rowcount or 0
    logger.info("  %d filas", rows)
    return rows


# =============================================================================
# DIM_VARIANT
# =============================================================================

TRANSFORM_DIM_VARIANT_SQL = text(
    """
    INSERT INTO analytical.dim_variant (
        variant_key,
        variant_id,
        sku,
        product_key,
        size,
        color
    )
    SELECT
        ROW_NUMBER() OVER (ORDER BY v.sku)::int AS variant_key,
        v.id AS variant_id,
        v.sku,
        p.product_key,
        v.size,
        v.color
    FROM staging.product_variants v
    INNER JOIN analytical.dim_product p ON p.product_id = v.product_id
    """
)


def transform_dim_variant(db: Session) -> int:
    """Carga las 647 variantes. Requiere dim_product cargada."""
    logger.info("→ analytical.dim_variant")
    db.execute(text("TRUNCATE TABLE analytical.dim_variant CASCADE"))
    result = db.execute(TRANSFORM_DIM_VARIANT_SQL)
    db.flush()
    rows = result.rowcount or 0
    logger.info("  %d filas", rows)
    return rows


# =============================================================================
# DIM_CUSTOMER
# =============================================================================

TRANSFORM_DIM_CUSTOMER_SQL = text(
    """
    INSERT INTO analytical.dim_customer (
        customer_key,
        customer_id,
        customer_code,
        full_name,
        email,
        age,
        age_group,
        gender,
        profile,
        channel_preference,
        preferred_segment,
        price_sensitivity,
        state_key,
        city,
        postal_code,
        signup_date,
        is_active
    )
    SELECT
        ROW_NUMBER() OVER (ORDER BY c.customer_code)::int AS customer_key,
        c.id AS customer_id,
        c.customer_code,
        c.first_name || ' ' || c.last_name AS full_name,
        c.email,
        c.age,
        CASE
            WHEN c.age < 25 THEN '<25'
            WHEN c.age < 35 THEN '25-34'
            WHEN c.age < 45 THEN '35-44'
            WHEN c.age < 55 THEN '45-54'
            ELSE '55+'
        END AS age_group,
        c.gender,
        c.profile,
        c.channel_preference,
        c.preferred_segment,
        c.price_sensitivity,
        s.state_key,
        c.city,
        c.postal_code,
        c.signup_date,
        CASE WHEN c.status = 'ACTIVE' THEN TRUE ELSE FALSE END AS is_active
    FROM staging.customers c
    INNER JOIN analytical.dim_state s ON s.state_id = c.state_id
    """
)


def transform_dim_customer(db: Session) -> int:
    """Carga los 10,000 clientes. Requiere dim_state cargada."""
    logger.info("→ analytical.dim_customer")
    db.execute(text("TRUNCATE TABLE analytical.dim_customer CASCADE"))
    result = db.execute(TRANSFORM_DIM_CUSTOMER_SQL)
    db.flush()
    rows = result.rowcount or 0
    logger.info("  %d filas", rows)
    return rows


# =============================================================================
# DIM_WAREHOUSE
# =============================================================================

TRANSFORM_DIM_WAREHOUSE_SQL = text(
    """
    INSERT INTO analytical.dim_warehouse (
        warehouse_key,
        location_id,
        code,
        name,
        location_type,
        state_key
    )
    SELECT
        ROW_NUMBER() OVER (ORDER BY l.code)::int AS warehouse_key,
        l.id AS location_id,
        l.code,
        l.name,
        l.location_type,
        s.state_key
    FROM staging.locations l
    INNER JOIN analytical.dim_state s ON s.state_id = l.state_id
    """
)


def transform_dim_warehouse(db: Session) -> int:
    """Carga las 15 ubicaciones. Requiere dim_state cargada."""
    logger.info("→ analytical.dim_warehouse")
    db.execute(text("TRUNCATE TABLE analytical.dim_warehouse CASCADE"))
    result = db.execute(TRANSFORM_DIM_WAREHOUSE_SQL)
    db.flush()
    rows = result.rowcount or 0
    logger.info("  %d filas", rows)
    return rows


# =============================================================================
# FACT_SALES
# =============================================================================

TRANSFORM_FACT_SALES_SQL = text(
    """
    INSERT INTO analytical.fact_sales (
        date_key,
        customer_key,
        product_key,
        variant_key,
        state_key,
        warehouse_key,
        order_id,
        order_number,
        channel,
        quantity,
        unit_price,
        discount,
        subtotal,
        created_at
    )
    SELECT
        TO_CHAR(o.order_date, 'YYYYMMDD')::int AS date_key,
        dc.customer_key,
        dp.product_key,
        dv.variant_key,
        ds.state_key,
        dw.warehouse_key,
        o.id AS order_id,
        o.order_number,
        o.channel,
        oi.quantity,
        oi.unit_price,
        oi.discount,
        oi.subtotal,
        o.created_at
    FROM staging.order_items oi
    INNER JOIN staging.orders o ON o.id = oi.order_id
    INNER JOIN staging.product_variants v ON v.id = oi.variant_id
    INNER JOIN analytical.dim_product dp ON dp.product_id = v.product_id
    INNER JOIN analytical.dim_variant dv ON dv.variant_id = oi.variant_id
    INNER JOIN analytical.dim_customer dc ON dc.customer_id = o.customer_id
    INNER JOIN analytical.dim_state ds ON ds.state_id = o.state_id
    INNER JOIN analytical.dim_warehouse dw ON dw.location_id = o.location_id
    """
)


def transform_fact_sales(db: Session) -> int:
    """Carga el hecho de ventas. Requiere TODAS las dims cargadas."""
    logger.info("→ analytical.fact_sales")
    db.execute(text("TRUNCATE TABLE analytical.fact_sales CASCADE"))
    result = db.execute(TRANSFORM_FACT_SALES_SQL)
    db.flush()
    rows = result.rowcount or 0
    logger.info("  %d filas", rows)
    return rows


# =============================================================================
# ORQUESTADOR
# =============================================================================

TRANSFORMERS = {
    "dim_date": transform_dim_date,
    "dim_state": transform_dim_state,
    "dim_product": transform_dim_product,
    "dim_variant": transform_dim_variant,
    "dim_customer": transform_dim_customer,
    "dim_warehouse": transform_dim_warehouse,
    "fact_sales": transform_fact_sales,
    "fact_shipments": transform_fact_shipments,
}

TRANSFORM_ORDER = [
    "dim_date",
    "dim_state",
    "dim_product",
    "dim_variant",
    "dim_customer",
    "dim_warehouse",
    "fact_sales",
    "fact_shipments",
]


def transform_all(db: Session, entities: list[str] | None = None) -> dict[str, int]:
    """Transforma todas las entidades ANALYTICAL.

    Si se especifican entidades, se respeta el orden de dependencias
    entre las que se pidan.
    """
    if entities is None:
        entities = list(TRANSFORM_ORDER)
    else:
        # Respetar el orden de TRANSFORM_ORDER entre las que se pidan
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