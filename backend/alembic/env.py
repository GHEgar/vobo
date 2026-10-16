from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import Connection
from sqlalchemy.pool import NullPool

import app.models  # noqa: F401
from app.core.database import URL_BASE, Base
from app.core.migraciones import motor_transaccional

config = context.config
externa = config.attributes.get("connection")

if config.config_file_name is not None and externa is None:
    fileConfig(config.config_file_name)

OPCIONES = {"target_metadata": Base.metadata, "render_as_batch": True, "compare_type": True}


def correr_offline() -> None:
    context.configure(url=URL_BASE, literal_binds=True, **OPCIONES)
    with context.begin_transaction():
        context.run_migrations()


def correr(conexion: Connection) -> None:
    context.configure(connection=conexion, **OPCIONES)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    correr_offline()
elif externa is not None:
    correr(externa)
else:
    motor = motor_transaccional(URL_BASE, poolclass=NullPool)
    try:
        with motor.begin() as conexion:
            correr(conexion)
    finally:
        motor.dispose()
