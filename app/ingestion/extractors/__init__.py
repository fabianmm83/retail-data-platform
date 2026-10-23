"""Extractores de datos desde el simulador."""

from app.ingestion.extractors.customers import extract_customers
from app.ingestion.extractors.locations import extract_locations
from app.ingestion.extractors.order_items import extract_order_items
from app.ingestion.extractors.orders import extract_orders
from app.ingestion.extractors.product_variants import extract_product_variants
from app.ingestion.extractors.products import extract_products
from app.ingestion.extractors.states import extract_states

__all__ = [
    "extract_customers",
    "extract_locations",
    "extract_order_items",
    "extract_orders",
    "extract_product_variants",
    "extract_products",
    "extract_states",
]