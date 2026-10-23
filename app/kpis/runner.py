"""Runner de la capa KPIS."""

from __future__ import annotations

import logging
import secrets
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.kpis.transformers import TRANSFORM_ORDER, transform_all
from app.meta.pipeline_runs import PipelineRun


logger = logging.getLogger(__name__)


def generate_kpi_run_id() -> str:
    """KPI-YYYYMMDD-HHMMSS-8hex."""
    now = datetime.utcnow()
    suffix = secrets.token_hex(4)
    return f"KPI-{now:%Y%m%d}-{now:%H%M%S}-{suffix}"


def run_kpis(
    *,
    db: Session,
    entities: list[str] | None = None,
) -> str:
    run_id = generate_kpi_run_id()

    if entities is None:
        entities = list(TRANSFORM_ORDER)

    run = PipelineRun(
        run_id=run_id,
        status="RUNNING",
        entities_processed=",".join(entities),
    )
    db.add(run)
    db.commit()

    logger.info("KPI run: %s", run_id)
    logger.info("Entidades: %s", entities)

    total_rows = 0

    try:
        results = transform_all(db, entities=entities)
        total_rows = sum(results.values())

        run.status = "SUCCESS"
        run.finished_at = datetime.utcnow()
        run.rows_ingested = total_rows
        db.commit()

        logger.info("KPI completado: %d filas totales", total_rows)
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

        logger.exception("KPI falló: %s", exc)
        raise