"""Base declarativa de SQLAlchemy para el data platform."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarativa común a todos los modelos del data platform."""

    pass


# Importar TODOS los modelos para que Alembic los detecte.
# A medida que agreguemos capas, se agregan más imports.
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