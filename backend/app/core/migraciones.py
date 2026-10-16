from pathlib import Path
from sqlite3 import Connection as ConexionSqlite

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, create_engine, event, inspect
from sqlalchemy.engine import URL, Connection
from sqlalchemy.pool import ConnectionPoolEntry, NullPool, StaticPool

from app.core import adopcion

CARPETA_ALEMBIC = Path(__file__).resolve().parents[2] / "alembic"
REVISION_BASE = "0001"


class EsquemaIncompatible(RuntimeError):
    pass


def configuracion(conexion: Connection | None = None) -> Config:
    config = Config()
    config.set_main_option("script_location", str(CARPETA_ALEMBIC))
    if conexion is not None:
        config.attributes["connection"] = conexion
    return config


def _sin_llaves_foraneas(conexion: ConexionSqlite, _registro: ConnectionPoolEntry) -> None:
    conexion.isolation_level = None
    conexion.execute("PRAGMA foreign_keys=OFF")


def _comenzar(conexion: Connection) -> None:
    conexion.exec_driver_sql("BEGIN IMMEDIATE")


def motor_transaccional(url: str | URL, **opciones: object) -> Engine:
    motor = create_engine(url, connect_args={"timeout": 30}, **opciones)
    event.listen(motor, "connect", _sin_llaves_foraneas)
    event.listen(motor, "begin", _comenzar)
    return motor


def esquema_base() -> adopcion.EsquemaBase:
    motor = motor_transaccional("sqlite://", poolclass=StaticPool)
    try:
        with motor.begin() as conexion:
            command.upgrade(configuracion(conexion), REVISION_BASE)
            return adopcion.leer_esquema(conexion)
    finally:
        motor.dispose()


def diferencias(conexion: Connection, base: adopcion.EsquemaBase) -> list[str]:
    contexto = MigrationContext.configure(conexion, opts={"compare_type": True})
    encontradas = [repr(d) for d in compare_metadata(contexto, base.metadata)]
    actuales = adopcion.checks_de(conexion, list(base.checks))
    for tabla, esperados in base.checks.items():
        if actuales.get(tabla, set()) != esperados:
            encontradas.append(f"CHECK distintos en {tabla}: {sorted(actuales.get(tabla, []))}")
    return encontradas


def adoptar(conexion: Connection) -> None:
    base = esquema_base()
    adopcion.renombrar_sub(conexion)
    adopcion.crear_tablas_faltantes(conexion, base)
    adopcion.asegurar_columnas(conexion)
    adopcion.asegurar_valores(conexion, base)
    adopcion.crear_indices_faltantes(conexion, base)
    encontradas = diferencias(conexion, base)
    if encontradas:
        raise EsquemaIncompatible(
            f"La base no coincide con la revisión {REVISION_BASE} tras las migraciones a mano; "
            "no se aplicó ningún cambio. Diferencias:\n  " + "\n  ".join(encontradas)
        )
    command.stamp(configuracion(conexion), REVISION_BASE)


def _llaves_rotas(conexion: Connection) -> list[tuple[object, ...]]:
    return [tuple(fila) for fila in conexion.exec_driver_sql("PRAGMA foreign_key_check")]


def migrar(motor: Engine) -> None:
    transaccional = motor_transaccional(motor.url, poolclass=NullPool)
    try:
        with transaccional.begin() as conexion:
            rotas_antes = _llaves_rotas(conexion)
            tablas = set(inspect(conexion).get_table_names())
            if tablas and "alembic_version" not in tablas:
                adoptar(conexion)
            command.upgrade(configuracion(conexion), "head")
            rotas = _llaves_rotas(conexion)
            if len(rotas) > len(rotas_antes):
                raise EsquemaIncompatible(
                    f"La migración dejaría {len(rotas) - len(rotas_antes)} llaves foráneas "
                    f"rotas; no se aplicó ningún cambio: {rotas[:10]}"
                )
    finally:
        transaccional.dispose()


def revision_actual(motor: Engine) -> str | None:
    with motor.connect() as conexion:
        return MigrationContext.configure(conexion).get_current_revision()


def revision_head() -> str | None:
    return ScriptDirectory.from_config(configuracion()).get_current_head()
