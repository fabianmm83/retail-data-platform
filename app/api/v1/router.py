"""Router principal de la API v1."""

from fastapi import APIRouter

from app.api.v1 import health, kpis


router = APIRouter()

router.include_router(health.router)
router.include_router(kpis.router, prefix="/api/v1")