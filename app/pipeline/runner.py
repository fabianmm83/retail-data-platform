"""Orquestador del pipeline."""

from __future__ import annotations

import logging
import secrets
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ingestion.extractors import (
    extract_categories,
    extract_customers,
    extract_locations,
    extract_order_items,
    extract_orders,
    extract_product_variants,
    extract_products,
    extract_states,
)
from app.ingestion.loader import RawLoader
from app.ingestion.watermark_store import WatermarkStore
from app.meta.pipeline_runs import PipelineRun
from app.raw.categories import RawCategory
from app.raw.customers import RawCustomer
from app.raw.locations import RawLocation
from app.raw.order_items import RawOrderItem
from app.raw.orders import RawOrder
from app.raw.product_variants import RawProductVariant
from app.raw.products import RawProduct
from app.raw.states import RawState


logger = logging.getLogger(__name__)


ENTITIES = {
    "categories": {
        "raw_model": RawCategory,
        "source_table": "categories",
        "mode": "full",
        "extractor": extract_categories,
    },
    "states": {
        "raw_model": RawState,
        "source_table": "states",
        "mode": "full",
        "extractor": extract_states,
    },
    "locations": {
        "raw_model": RawLocation,
        "source_table": "locations",
        "mode": "full",
        "extractor": extract_locations,
    },
    "products": {
        "raw_model": RawProduct,
        "source_table": "products",
        "mode": "full",
        "extractor": extract_products,
    },
    "product_variants": {
        "raw_model": RawProductVariant,
        "source_table": "product_variants",
        "mode": "full",
        "extractor": extract_product_variants,
    },
    "customers": {
        "raw_model": RawCustomer,
        "source_table": "customers",
        "mode": "full",
        "extractor": extract_customers,
    },
    "orders": {
        "raw_model": RawOrder,
        "source_table": "orders",
        "mode": "incremental",
        "extractor": extract_orders,
    },
    "order_items": {
        "raw_model": RawOrderItem,
        "source_table": "order_items",
        "mode": "incremental",
        "extractor": extract_order_items,
    },
}


def generate_run_id() -> str:
    now = datetime.utcnow()
    suffix = secrets.token_hex(4)
    return f"ING-{now:%Y%m%d}-{now:%H%M%S}-{suffix}"


def _run_entity(
    *,
    entity_name: str,
    source_db: Session,
    target_db: Session,
    run_id: str,
) -> int:
    config = ENTITIES[entity_name]
    raw_model = config["raw_model"]
    source_table = config["source_table"]
    mode = config["mode"]
    extractor = config["extractor"]

    loader = RawLoader(target_db, run_id=run_id)
    watermark_store = WatermarkStore(target_db)

    logger.info("→ %s (mode=%s)", entity_name, mode)

    watermark_store.mark_running(entity_name)

    if mode == "full":
        rows = extractor(source_db=source_db)
        last_date = None
        last_id = None
    else:
        rows, last_date, last_id = extractor(
            source_db=source_db,
            watermark_store=watermark_store,
        )

    logger.info("  extraídas %d filas", len(rows))

    processed = loader.upsert_many(
        model=raw_model,
        rows=rows,
        source_table=source_table,
    )

    watermark_store.update(
        entity_name=entity_name,
        last_date=last_date,
        last_id=last_id,
        rows=processed,
    )

    logger.info("  %d filas procesadas", processed)
    return processed


def run_pipeline(
    *,
    source_db: Session,
    target_db: Session,
    entities: list[str],
) -> str:
    if entities == ["all"]:
        entities = list(ENTITIES.keys())

    for entity in entities:
        if entity not in ENTITIES:
            raise ValueError(
                f"Entidad desconocida: {entity}. "
                f"Válidas: {list(ENTITIES.keys())}"
            )

    run_id = generate_run_id()

    run = PipelineRun(
        run_id=run_id,
        status="RUNNING",
        entities_processed=",".join(entities),
    )
    target_db.add(run)
    target_db.commit()

    logger.info("Run: %s", run_id)
    logger.info("Entidades: %s", entities)

    total_rows = 0

    try:
        for entity in entities:
            processed = _run_entity(
                entity_name=entity,
                source_db=source_db,
                target_db=target_db,
                run_id=run_id,
            )
            total_rows += processed

        run.status = "SUCCESS"
        run.finished_at = datetime.utcnow()
        run.rows_ingested = total_rows
        target_db.commit()

        logger.info("Run completado: %d filas totales", total_rows)
        return run_id

    except Exception as exc:
        target_db.rollback()

        run_obj = target_db.scalar(
            select(PipelineRun).where(PipelineRun.run_id == run_id)
        )
        if run_obj is not None:
            run_obj.status = "FAILED"
            run_obj.finished_at = datetime.utcnow()
            run_obj.error_message = str(exc)
            target_db.commit()

        logger.exception("Pipeline falló: %s", exc)
        raise