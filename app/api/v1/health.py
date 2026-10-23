"""Endpoints de health check."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.kpis import HealthResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="retail-data-platform",
        database="postgresql",
    )


@router.get("/health/database", response_model=HealthResponse)
def database_health_check(db: Session = Depends(get_db)) -> HealthResponse:
    db.execute(text("SELECT 1"))
    return HealthResponse(
        status="ok",
        service="retail-data-platform",
        database="postgresql",
    )