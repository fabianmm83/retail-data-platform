"""Extractor incremental de órdenes por order_date."""

from datetime import date
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.ingestion.watermark_store import WatermarkStore


def extract_orders(
    *,
    source_db: Session,
    watermark_store: WatermarkStore,
) -> tuple[list[dict[str, Any]], date | None, str | None]:
    """Extrae órdenes nuevas desde el último watermark.

    Returns:
        (rows, last_order_date, last_order_number)
    """
    watermark_date = watermark_store.get_watermark_date("orders")
    watermark_id = watermark_store.get_watermark_id("orders")

    # Si no hay watermark_id previo, usar string vacío para evitar
    # el problema de AmbiguousParameter con NULL.
    wid = watermark_id if watermark_id is not None else ""

    sql = text(
        """
        SELECT
            id,
            order_number,
            customer_id,
            state_id,
            location_id,
            channel::text AS channel,
            status::text AS status,
            order_date,
            payment_method::text AS payment_method,
            paid,
            subtotal,
            discount,
            shipping_cost,
            total,
            created_at,
            updated_at
        FROM orders
        WHERE
            order_date > :wdate
            OR (order_date = :wdate AND order_number > :wid)
        ORDER BY order_date, order_number
        """
    )

    result = source_db.execute(
        sql,
        {"wdate": watermark_date, "wid": wid},
    ).mappings().all()

    rows = [dict(r) for r in result]

    if rows:
        last_date = rows[-1]["order_date"]
        last_id = rows[-1]["order_number"]
    else:
        last_date = None
        last_id = None

    return rows, last_date, last_id