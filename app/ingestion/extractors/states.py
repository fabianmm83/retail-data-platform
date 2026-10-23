"""Extractor de estados (full load).

Solo 10 filas. No vale la pena incremental.
"""

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


def extract_states(*, source_db: Session) -> list[dict[str, Any]]:
    """Extrae TODOS los estados del simulador."""
    sql = text(
        """
        SELECT
            id,
            code,
            name,
            region::text AS region,
            income_group::text AS income_group,
            population_share,
            income_index,
            online_penetration,
            regional_factor,
            growth_rate,
            status::text AS status,
            created_at,
            updated_at
        FROM states
        ORDER BY code
        """
    )
    rows = source_db.execute(sql).mappings().all()
    return [dict(r) for r in rows]