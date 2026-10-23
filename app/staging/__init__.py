"""Modelos y transformadores de la capa STAGING."""

from app.staging.customers import StagingCustomer
from app.staging.order_items import StagingOrderItem
from app.staging.orders import StagingOrder
from app.staging.runner import run_staging
from app.staging.transformers import (
    transform_all,
    transform_customers,
    transform_order_items,
    transform_orders,
)

__all__ = [
    # Modelos
    "StagingCustomer",
    "StagingOrder",
    "StagingOrderItem",
    # Transformadores
    "transform_all",
    "transform_customers",
    "transform_orders",
    "transform_order_items",
    # Runner
    "run_staging",
]