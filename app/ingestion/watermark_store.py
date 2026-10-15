"""Gestión de watermarks.

Un watermark por entidad. Dice hasta dónde se ha ingestado cada tabla
del origen.

Uso típico:

    wm = WatermarkStore(db)

    # Leer watermark actual
    last_date = wm.get_watermark_date("orders")  # → date | None

    # ... hacer la extracción ...

    # Actualizar watermark después de la ingesta exitosa
    wm.update_watermark(
        entity_name="orders",
        last_date=date(2026, 5, 15),
        last_id="ORDER-2026-003421",
        rows=188,
    )
"""

from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.meta.watermark import Watermark


# Fecha por defecto cuando no hay watermark previo.
# Traer desde muy atrás para capturar todo.
DEFAULT_WATERMARK_DATE = date(1900, 1, 1)


class WatermarkStore:
    """Wrapper sobre la tabla meta.watermarks."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ---------------------------------------------------------------------
    # Lectura
    # ---------------------------------------------------------------------

    def get(self, entity_name: str) -> Watermark | None:
        """Devuelve el watermark de una entidad o None si no existe."""
        stmt = select(Watermark).where(Watermark.entity_name == entity_name)
        return self.db.scalar(stmt)

    def get_watermark_date(self, entity_name: str) -> date:
        """Devuelve la fecha del watermark. Default: 1900-01-01 si no existe."""
        wm = self.get(entity_name)
        if wm is None or wm.last_watermark_date is None:
            return DEFAULT_WATERMARK_DATE
        return wm.last_watermark_date

    def get_watermark_id(self, entity_name: str) -> str | None:
        """Devuelve el último id ingestado. None si no existe."""
        wm = self.get(entity_name)
        if wm is None:
            return None
        return wm.last_watermark_id

    # ---------------------------------------------------------------------
    # Escritura
    # ---------------------------------------------------------------------

    def mark_running(self, entity_name: str) -> None:
        """Marca el watermark como RUNNING (antes de empezar la ingesta)."""
        wm = self.get(entity_name)
        if wm is None:
            wm = Watermark(entity_name=entity_name)
            self.db.add(wm)
        wm.status = "RUNNING"
        wm.last_run_at = datetime.utcnow()
        self.db.flush()

    def update(
        self,
        *,
        entity_name: str,
        last_date: date | None,
        last_id: str | None,
        rows: int,
    ) -> None:
        """Actualiza el watermark después de una ingesta exitosa."""
        wm = self.get(entity_name)
        if wm is None:
            wm = Watermark(entity_name=entity_name)
            self.db.add(wm)

        if last_date is not None:
            wm.last_watermark_date = last_date
        if last_id is not None:
            wm.last_watermark_id = last_id

        wm.rows_last_run = rows
        wm.last_run_at = datetime.utcnow()
        wm.status = "SUCCESS"
        self.db.flush()

    def mark_failed(self, entity_name: str, error: str | None = None) -> None:
        """Marca el watermark como FAILED."""
        wm = self.get(entity_name)
        if wm is None:
            wm = Watermark(entity_name=entity_name)
            self.db.add(wm)
        wm.status = "FAILED"
        wm.last_run_at = datetime.utcnow()
        self.db.flush()