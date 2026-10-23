"""Runner de la capa STAGING.

Ejecuta la transformación RAW → STAGING y registra el resultado
en meta.pipeline_runs (reusa la tabla de control del pipeline).

Uso:

    from app.db.session import TargetSessionLocal
    from app.staging.runner import run_staging

    with TargetSessionLocal() as db:
        run_id = run_staging(db, entities=['customers', 'orders', 'order_items'])
"""

from __future__ import annotations

import logging
import secrets
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.meta.pipeline_runs import PipelineRun
from app.staging.transformers import transform_all


logger = logging.getLogger(__name__)


# =============================================================================
# RUN ID
# =============================================================================


def generate_staging_run_id() -> str:
    """Genera un run_id para STAGING: STG-YYYYMMDD-HHMMSS-8hex."""
    now = datetime.utcnow()
    suffix = secrets.token_hex(4)
    return f"STG-{now:%Y%m%d}-{now:%H%M%S}-{suffix}"


# =============================================================================
# ORQUESTADOR
# =============================================================================


def run_staging(
    *,
    db: Session,
    entities: list[str] | None = None,
) -> str:
    """Ejecuta la transformación RAW → STAGING.

    Args:
        db: sesión al data platform.
        entities: lista de entidades a transformar (None = todas).

    Returns:
        El run_id generado.
    """
    run_id = generate_staging_run_id()

    if entities is None:
        entities = ["customers", "orders", "order_items"]

    # Registrar el run
    run = PipelineRun(
        run_id=run_id,
        status="RUNNING",
        entities_processed=",".join(entities),
    )
    db.add(run)
    db.commit()

    logger.info("Staging run: %s", run_id)
    logger.info("Entidades: %s", entities)

    total_rows = 0

    try:
        results = transform_all(db, entities=entities)
        total_rows = sum(results.values())

        # Marcar run como SUCCESS
        run.status = "SUCCESS"
        run.finished_at = datetime.utcnow()
        run.rows_ingested = total_rows
        db.commit()

        logger.info("Staging completado: %d filas totales", total_rows)
        return run_id

    except Exception as exc:
        db.rollback()

        # Marcar run como FAILED
        run_obj = db.scalar(
            select(PipelineRun).where(PipelineRun.run_id == run_id)
        )
        if run_obj is not None:
            run_obj.status = "FAILED"
            run_obj.finished_at = datetime.utcnow()
            run_obj.error_message = str(exc)
            db.commit()

        logger.exception("Staging falló: %s", exc)
        raise