"""Base declarativa de SQLAlchemy para el data platform."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarativa común a todos los modelos del data platform."""

    pass


from app.analytical import (  # noqa: E402, F401
    dim_customer as _an_dim_customer,
    dim_date as _an_dim_date,
    dim_product as _an_dim_product,
    dim_state as _an_dim_state,
    dim_variant as _an_dim_variant,
    dim_warehouse as _an_dim_warehouse,
    fact_sales as _an_fact_sales,
    fact_shipments as _an_fact_shipments,
)
from app.kpis import (  # noqa: E402, F401
    logistics_performance as _kpi_logistics,
    revenue_by_channel as _kpi_rev_chan,
    revenue_by_product as _kpi_rev_prod,
    revenue_by_state as _kpi_rev_state,
    revenue_daily as _kpi_rev_daily,
)
from app.meta import pipeline_runs as _meta_pipeline_runs  # noqa: E402, F401
from app.meta import watermark as _meta_watermark  # noqa: E402, F401
from app.raw import (  # noqa: E402, F401
    carriers,
    categories,
    customers,
    inventory_movements,
    locations,
    order_items,
    orders,
    product_variants,
    products,
    shipments,
    states,
)
from app.staging import (  # noqa: E402, F401
    categories as _stg_categories,
    customers as _stg_customers,
    locations as _stg_locations,
    order_items as _stg_order_items,
    orders as _stg_orders,
    product_variants as _stg_product_variants,
    products as _stg_products,
    shipments as _stg_shipments,
    states as _stg_states,
)