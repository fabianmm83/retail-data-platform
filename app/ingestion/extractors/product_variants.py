"""Extractor de variantes de producto (full load).

647 filas. Full load.
"""

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


def extract_product_variants(*, source_db: Session) -> list[dict[str, Any]]:
    """Extrae TODAS las variantes (SKUs)."""
    sql = text(
        """
        SELECT
            id,
            sku,
            product_id,
            size,
            color::text AS color,
            barcode,
            status::text AS status,
            created_at,
            updated_at
        FROM product_variants
        ORDER BY sku
        """
    )
    rows = source_db.execute(mapping_sql := sql).mappings().all()
    return [dict(r) for r in rows]