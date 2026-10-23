"""Modelos y transformadores de la capa STAGING."""

from app.staging.customers import StagingCustomer
from app.staging.locations import StagingLocation
from app.staging.order_items import StagingOrderItem
from app.staging.orders import StagingOrder
from app.staging.product_variants import StagingProductVariant
from app.staging.products import StagingProduct
from app.staging.runner import run_staging
from app.staging.states import StagingState
from app.staging.transformers import (
    transform_all,
    transform_customers,
    transform_locations,
    transform_order_items,
    transform_orders,
    transform_product_variants,
    transform_products,
    transform_states,
)

__all__ = [
    # Modelos
    "StagingCustomer",
    "StagingLocation",
    "StagingOrderItem",
    "StagingOrder",
    "StagingProductVariant",
    "StagingProduct",
    "StagingState",
    # Transformadores
    "transform_all",
    "transform_customers",
    "transform_locations",
    "transform_order_items",
    "transform_orders",
    "transform_product_variants",
    "transform_products",
    "transform_states",
    # Runner
    "run_staging",
]