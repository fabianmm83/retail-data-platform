"""Runner de la capa ANALYTICAL.

Ejecuta la transformación STAGING → ANALYTICAL y registra el resultado
en meta.pipeline_runs.

Uso:

    from app.db.session import TargetSessionLocal
    from app.analytical.runner import run_analytical

    with TargetSessionLocal() as db:
        run_id = run_analytical(db)
"""

from __future__ import annotations

import logging
import secrets
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytical.transformers import TRANSFORM_ORDER, transform_all
from app.meta.pipeline_runs import PipelineRun


logger = logging.getLogger(__name__)


# =============================================================================
# RUN ID
# =============================================================================


def generate_analytical_run_id() -> str:
    """Genera un run_id para ANALYTICAL: ANL-YYYYMMDD-HHMMSS-8hex."""
    now = datetime.utcnow()
    suffix = secrets.token_hex(4)
    return f"ANL-{now:%Y%m%d}-{now:%H%M%S}-{suffix}"


# =============================================================================
# ORQUESTADOR
# =============================================================================


def run_analytical(
    *,
    db: Session,
    entities: list[str] | None = None,
) -> str:
    """Ejecuta la transformación STAGING → ANALYTICAL.

    Args:
        db: sesión al data platform.
        entities: lista de entidades a transformar (None = todas, en orden).

    Returns:
        El run_id generado.
    """
    run_id = generate_analytical_run_id()

    if entities is None:
        entities = list(TRANSFORM_ORDER)

    run = PipelineRun(
        run_id=run_id,
        status="RUNNING",
        entities_processed=",".join(entities),
    )
    db.add(run)
    db.commit()

    logger.info("Analytical run: %s", run_id)
    logger.info("Entidades: %s", entities)

    total_rows = 0

    try:
        results = transform_all(db, entities=entities)
        total_rows = sum(results.values())

        run.status = "SUCCESS"
        run.finished_at = datetime.utcnow()
        run.rows_ingested = total_rows
        db.commit()

        logger.info("Analytical completado: %d filas totales", total_rows)
        return run_id

    except Exception as exc:
        db.rollback()

        run_obj = db.scalar(
            select(PipelineRun).where(PipelineRun.run_id == run_id)
        )
        if run_obj is not None:
            run_obj.status = "FAILED"
            run_obj.finished_at = datetime.utcnow()
            run_obj.error_message = str(exc)
            db.commit()

        logger.exception("Analytical falló: %s", exc)
        raise