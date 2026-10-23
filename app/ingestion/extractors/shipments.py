"""Extractor de shipments (incremental por updated_at)."""

from datetime import date
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.ingestion.watermark_store import WatermarkStore


def extract_shipments(
    *,
    source_db: Session,
    watermark_store: WatermarkStore,
) -> tuple[list[dict[str, Any]], date | None, str | None]:
    """Extrae shipments nuevos o modificados desde el último watermark.

    Usa `updated_at` como criterio incremental porque el status
    cambia a lo largo del ciclo de vida del shipment.
    """
    watermark_date = watermark_store.get_watermark_date("shipments")

    sql = text(
        """
        SELECT
            id,
            shipment_number,
            tracking_number,
            order_id,
            carrier_id,
            origin_location_id,
            status::text AS status,
            shipped_at,
            estimated_delivery,
            delivered_at,
            shipping_cost,
            weight_kg,
            created_at,
            updated_at
        FROM shipments
        WHERE DATE(updated_at) >= :wdate
        ORDER BY updated_at, shipment_number
        """
    )

    result = source_db.execute(
        sql,
        {"wdate": watermark_date},
    ).mappings().all()

    rows = [dict(r) for r in result]

    if rows:
        last_date = rows[-1]["updated_at"].date()
        last_id = rows[-1]["shipment_number"]
    else:
        last_date = None
        last_id = None

    return rows, last_date, last_id