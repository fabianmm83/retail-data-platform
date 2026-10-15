"""Extractor incremental de order_items.

Los items no tienen fecha propia. Se extraen por su orden padre.
"""

from datetime import date
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.ingestion.watermark_store import WatermarkStore


def extract_order_items(
    *,
    source_db: Session,
    watermark_store: WatermarkStore,
) -> tuple[list[dict[str, Any]], date | None, str | None]:
    """Extrae order_items de órdenes nuevas."""
    watermark_date = watermark_store.get_watermark_date("order_items")
    watermark_id = watermark_store.get_watermark_id("order_items")

    wid = watermark_id if watermark_id is not None else ""

    sql = text(
        """
        SELECT
            oi.id,
            oi.order_id,
            oi.variant_id,
            oi.quantity,
            oi.unit_price,
            oi.discount,
            oi.subtotal,
            oi.created_at,
            oi.updated_at,
            o.order_date       AS _order_date,
            o.order_number     AS _order_number
        FROM order_items oi
        INNER JOIN orders o ON o.id = oi.order_id
        WHERE
            o.order_date > :wdate
            OR (o.order_date = :wdate AND o.order_number > :wid)
        ORDER BY o.order_date, o.order_number, oi.id
        """
    )

    result = source_db.execute(
        sql,
        {"wdate": watermark_date, "wid": wid},
    ).mappings().all()

    rows = []
    for r in result:
        row = dict(r)
        row.pop("_order_date", None)
        row.pop("_order_number", None)
        rows.append(row)

    if result:
        last_date = result[-1]["_order_date"]
        last_id = result[-1]["_order_number"]
    else:
        last_date = None
        last_id = None

    return rows, last_date, last_id