"""Orquestador del pipeline.

Coordina las fases:

1. Genera un run_id único.
2. Registra el run en meta.pipeline_runs.
3. Por cada entidad solicitada:
   a. Marca el watermark como RUNNING.
   b. Extrae filas del origen.
   c. Carga las filas a RAW con UPSERT.
   d. Actualiza el watermark como SUCCESS.
4. Marca el run como SUCCESS o FAILED.
"""

from __future__ import annotations

import logging
import secrets
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ingestion.extractors import (
    extract_customers,
    extract_order_items,
    extract_orders,
)
from app.ingestion.loader import RawLoader
from app.ingestion.watermark_store import WatermarkStore
from app.meta.pipeline_runs import PipelineRun
from app.raw.customers import RawCustomer
from app.raw.order_items import RawOrderItem
from app.raw.orders import RawOrder


logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURACIÓN DE ENTIDADES
# =============================================================================

ENTITIES = {
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


# =============================================================================
# RUN ID
# =============================================================================


def generate_run_id() -> str:
    """Genera un run_id: ING-YYYYMMDD-HHMMSS-8hex."""
    now = datetime.utcnow()
    suffix = secrets.token_hex(4)  # 8 hex chars
    return f"ING-{now:%Y%m%d}-{now:%H%M%S}-{suffix}"


# =============================================================================
# EJECUCIÓN DE UNA ENTIDAD
# =============================================================================


def _run_entity(
    *,
    entity_name: str,
    source_db: Session,
    target_db: Session,
    run_id: str,
) -> int:
    """Ejecuta la ingesta de una entidad. Devuelve filas procesadas."""
    config = ENTITIES[entity_name]
    raw_model = config["raw_model"]
    source_table = config["source_table"]
    mode = config["mode"]
    extractor = config["extractor"]

    loader = RawLoader(target_db, run_id=run_id)
    watermark_store = WatermarkStore(target_db)

    logger.info("→ %s (mode=%s)", entity_name, mode)

    # 1. Marcar watermark RUNNING
    watermark_store.mark_running(entity_name)

    # 2. Extraer del origen
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

    # 3. Cargar a RAW
    processed = loader.upsert_many(
        model=raw_model,
        rows=rows,
        source_table=source_table,
    )

    # 4. Actualizar watermark
    watermark_store.update(
        entity_name=entity_name,
        last_date=last_date,
        last_id=last_id,
        rows=processed,
    )

    logger.info("  %d filas procesadas", processed)
    return processed


# =============================================================================
# ORQUESTADOR
# =============================================================================


def run_pipeline(
    *,
    source_db: Session,
    target_db: Session,
    entities: list[str],
) -> str:
    """Ejecuta el pipeline completo.

    Args:
        source_db: sesión al simulador (5434).
        target_db: sesión al data platform (5435).
        entities: lista de entidades a procesar (o ['all']).

    Returns:
        El run_id generado.
    """
    # Resolver "all"
    if entities == ["all"]:
        entities = list(ENTITIES.keys())

    # Validar
    for entity in entities:
        if entity not in ENTITIES:
            raise ValueError(
                f"Entidad desconocida: {entity}. "
                f"Válidas: {list(ENTITIES.keys())}"
            )

    run_id = generate_run_id()

    # Registrar el run
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

        # Marcar run como SUCCESS
        run.status = "SUCCESS"
        run.finished_at = datetime.utcnow()
        run.rows_ingested = total_rows
        target_db.commit()

        logger.info("Run completado: %d filas totales", total_rows)
        return run_id

    except Exception as exc:
        target_db.rollback()

        # Marcar run como FAILED
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