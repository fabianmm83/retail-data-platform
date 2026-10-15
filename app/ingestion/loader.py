"""Loader genérico para cargar filas a RAW.

Hace UPSERT por `_source_id` para que la ingesta sea idempotente.
"""

from datetime import datetime
from typing import Any

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.db.base import Base


class RawLoader:
    """Carga filas a una tabla RAW con UPSERT por _source_id."""

    def __init__(self, db: Session, run_id: str) -> None:
        self.db = db
        self.run_id = run_id

    def upsert_many(
        self,
        *,
        model: type[Base],
        rows: list[dict[str, Any]],
        source_table: str,
        batch_size: int = 500,
    ) -> int:
        """Carga filas con UPSERT por _source_id.

        Args:
            model: la clase ORM de la tabla RAW (ej. RawOrder).
            rows: lista de dicts con los campos de la tabla RAW (sin metadata).
            source_table: nombre de la tabla origen (ej. 'orders').
            batch_size: cuántas filas por batch.

        Returns:
            Cantidad de filas procesadas (insertadas o actualizadas).
        """
        if not rows:
            return 0

        processed = 0

        for i in range(0, len(rows), batch_size):
            batch = rows[i : i + batch_size]

            # Enriquecer con metadata
            enriched = []
            for row in batch:
                enriched_row = {
                    **row,
                    "_source_id": str(row["_source_id"]) if "_source_id" in row else str(row["id"]),
                    "_ingestion_run_id": self.run_id,
                    "_source_table": source_table,
                }
                enriched.append(enriched_row)

            stmt = pg_insert(model).values(enriched)

            # UPSERT: si el _source_id ya existe, actualiza todos los campos
            # menos _raw_id (que es PK autoincremental) y _ingested_at.
            update_cols = {
                col.name: stmt.excluded[col.name]
                for col in model.__table__.columns
                if col.name not in ("_raw_id", "_ingested_at")
            }

            stmt = stmt.on_conflict_do_update(
                index_elements=["_source_id"],
                set_=update_cols,
            )

            self.db.execute(stmt)
            processed += len(batch)

        self.db.flush()
        return processed