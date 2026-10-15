from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.db.base import Base

# =============================================================================
# IMPORTANTE: aquí se importarán todos los modelos del data platform
# a medida que los creamos. Por ahora no hay modelos, así que está vacío.
# Cuando agreguemos modelos, se importan aquí.
# =============================================================================

# Objeto de configuración de Alembic.
config = context.config

# Inyectar la URL del DESTINO (data platform).
config.set_main_option("sqlalchemy.url", settings.target_database_url)

# Configurar logging desde alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata para autogenerate.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Ejecuta migraciones en modo 'offline'."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecuta migraciones en modo 'online'."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_schemas=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()