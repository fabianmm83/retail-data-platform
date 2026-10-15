"""Configuración del data platform.

Lee variables de entorno desde .env. Expone dos URLs de conexión:

- source_database_url : PostgreSQL del simulador (origen, solo lectura)
- target_database_url : PostgreSQL del data platform (destino, lectura/escritura)
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Cuidado con Rikochet - Retail Data Platform"
    app_version: str = "0.1.0"
    app_env: str = "development"

    # --- Origen (simulador) ------------------------------------------------
    source_postgres_host: str
    source_postgres_port: int = 5434
    source_postgres_db: str
    source_postgres_user: str
    source_postgres_password: str
    source_database_url: str

    # --- Destino (analítica) -----------------------------------------------
    target_postgres_host: str
    target_postgres_port: int = 5435
    target_postgres_db: str
    target_postgres_user: str
    target_postgres_password: str
    target_database_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()