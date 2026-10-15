"""Extractor de clientes (full load) usando SQL puro."""

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


def extract_customers(*, source_db: Session) -> list[dict[str, Any]]:
    """Extrae TODOS los clientes del simulador.

    Devuelve una lista de dicts con los campos de raw.customers.
    """
    sql = text(
        """
        SELECT
            id,
            customer_code,
            first_name,
            last_name,
            email,
            phone,
            birth_date,
            gender::text AS gender,
            state_id,
            city,
            postal_code,
            profile::text AS profile,
            channel_preference::text AS channel_preference,
            preferred_segment::text AS preferred_segment,
            price_sensitivity::text AS price_sensitivity,
            signup_date,
            first_order_date,
            last_order_date,
            total_orders,
            total_revenue,
            total_units,
            status::text AS status,
            created_at,
            updated_at
        FROM customers
        ORDER BY customer_code
        """
    )
    rows = source_db.execute(sql).mappings().all()
    return [dict(row) for row in rows]