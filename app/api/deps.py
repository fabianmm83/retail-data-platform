"""Dependencias de FastAPI."""

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import TargetSessionLocal


def get_db() -> Generator[Session, None, None]:
    """Sesión de DB al data platform (destino)."""
    db = TargetSessionLocal()
    try:
        yield db
    finally:
        db.close()