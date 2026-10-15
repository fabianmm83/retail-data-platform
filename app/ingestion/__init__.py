"""Ingesta de datos desde el simulador al data platform."""

from app.ingestion.loader import RawLoader
from app.ingestion.watermark_store import WatermarkStore

__all__ = ["RawLoader", "WatermarkStore"]