"""Extractor de ubicaciones (full load).

15 filas. Full load.
"""

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


def extract_locations(*, source_db: Session) -> list[dict[str, Any]]:
    """Extrae TODAS las ubicaciones (CEDIS + tiendas)."""
    sql = text(
        """
        SELECT
            id,
            code,
            name,
            location_type::text AS location_type,
            state_id,
            capacity_units,
            status::text AS status,
            created_at,
            updated_at
        FROM locations
        ORDER BY code
        """
    )
    rows = source_db.execute(sql).mappings().all()
    return [dict(r) for r in rows]