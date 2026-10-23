"""Extractor de productos (full load).

32 filas. Full load.
"""

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


def extract_products(*, source_db: Session) -> list[dict[str, Any]]:
    """Extrae TODOS los productos del simulador."""
    sql = text(
        """
        SELECT
            id,
            style_code,
            name,
            segment::text AS segment,
            age_group::text AS age_group,
            category_id,
            sport::text AS sport,
            branded,
            base_price,
            base_cost,
            demand_profile::text AS demand_profile,
            lifecycle_stage::text AS lifecycle_stage,
            launch_date,
            status::text AS status,
            created_at,
            updated_at
        FROM products
        ORDER BY style_code
        """
    )
    rows = source_db.execute(sql).mappings().all()
    return [dict(r) for r in rows]