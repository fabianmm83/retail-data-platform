"""Conexiones a bases de datos.

Dos engines separados:

- `source_engine`: PostgreSQL del simulador (solo lectura).
- `target_engine`: PostgreSQL del data platform (lectura/escritura).
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


# =============================================================================
# ENGINE ORIGEN — Simulador (solo lectura)
# =============================================================================

source_engine = create_engine(
    settings.source_database_url,
    pool_pre_ping=True,
    future=True,
)

SourceSessionLocal = sessionmaker(
    bind=source_engine,
    class_=Session,
    autoflush=False,
    autocommit=False,
)


def get_source_db() -> Generator[Session, None, None]:
    """Sesión de solo lectura al operacional."""
    db = SourceSessionLocal()
    try:
        yield db
    finally:
        db.close()


# =============================================================================
# ENGINE DESTINO — Data platform (lectura/escritura)
# =============================================================================

target_engine = create_engine(
    settings.target_database_url,
    pool_pre_ping=True,
    future=True,
)

TargetSessionLocal = sessionmaker(
    bind=target_engine,
    class_=Session,
    autoflush=False,
    autocommit=False,
)


def get_target_db() -> Generator[Session, None, None]:
    """Sesión de lectura/escritura al data platform."""
    db = TargetSessionLocal()
    try:
        yield db
    finally:
        db.close()