"""Extractores de datos desde el simulador."""

from app.ingestion.extractors.customers import extract_customers
from app.ingestion.extractors.order_items import extract_order_items
from app.ingestion.extractors.orders import extract_orders

__all__ = [
    "extract_customers",
    "extract_order_items",
    "extract_orders",
]