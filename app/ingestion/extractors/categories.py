"""Extractor de categorías (full load).

12 filas. Full load.
"""

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


def extract_categories(*, source_db: Session) -> list[dict[str, Any]]:
    """Extrae TODAS las categorías del simulador."""
    sql = text(
        """
        SELECT
            id,
            code,
            name,
            department::text AS department,
            seasonality::text AS seasonality,
            status::text AS status,
            created_at,
            updated_at
        FROM categories
        ORDER BY code
        """
    )
    rows = source_db.execute(sql).mappings().all()
    return [dict(r) for r in rows]