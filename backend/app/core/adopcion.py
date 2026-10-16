from dataclasses import dataclass

from sqlalchemy import MetaData, inspect, text
from sqlalchemy.engine import Connection

COLUMNAS_AGREGADAS = {
    "resultados": {"comentario": "TEXT"},
    "usuarios": {"permisos": "JSON"},
    "fallas": {"seccion_id": "VARCHAR(120)", "tipo": "VARCHAR(10) NOT NULL DEFAULT 'falla'"},
    "sesiones": {"renovando_hasta": "DATETIME"},
}
VALORES_AGREGADOS = {"decisiones": "desplegar_con_aviso"}
COLUMNA_SUB = "sub_oidc"
SUFIJO_SUB_ANTERIOR = "_sub"


@dataclass(frozen=True)
class EsquemaBase:
    metadata: MetaData
    tablas: dict[str, str]
    indices: dict[str, tuple[str, str]]
    checks: dict[str, set[tuple[str | None, str]]]


def _sqlite_master(conexion: Connection) -> list[tuple[str, str, str, str | None]]:
    return [
        (tipo, nombre, tabla, sql)
        for tipo, nombre, tabla, sql in conexion.execute(
            text(
                "SELECT type, name, tbl_name, sql FROM sqlite_master "
                "WHERE tbl_name NOT LIKE 'sqlite_%' AND tbl_name != 'alembic_version'"
            )
        )
    ]


def leer_esquema(conexion: Connection) -> EsquemaBase:
    filas = _sqlite_master(conexion)
    tablas = {nombre: sql for tipo, nombre, _t, sql in filas if tipo == "table" and sql}
    indices = {
        nombre: (tabla, sql) for tipo, nombre, tabla, sql in filas if tipo == "index" and sql
    }
    metadata = MetaData()
    metadata.reflect(conexion, only=list(tablas))
    return EsquemaBase(
        metadata=metadata, tablas=tablas, indices=indices, checks=checks_de(conexion, list(tablas))
    )


def checks_de(conexion: Connection, tablas: list[str]) -> dict[str, set[tuple[str | None, str]]]:
    inspector = inspect(conexion)
    return {
        tabla: {
            (check["name"], "".join(check["sqltext"].split()))
            for check in inspector.get_check_constraints(tabla)
        }
        for tabla in tablas
        if inspector.has_table(tabla)
    }


def crear_tablas_faltantes(conexion: Connection, base: EsquemaBase) -> None:
    existentes = set(inspect(conexion).get_table_names())
    for tabla, sentencia in base.tablas.items():
        if tabla not in existentes:
            conexion.exec_driver_sql(sentencia)


def crear_indices_faltantes(conexion: Connection, base: EsquemaBase) -> None:
    existentes = {nombre for tipo, nombre, _t, _s in _sqlite_master(conexion) if tipo == "index"}
    for nombre, (_tabla, sentencia) in base.indices.items():
        if nombre not in existentes:
            conexion.exec_driver_sql(sentencia)


def asegurar_columnas(conexion: Connection) -> None:
    inspector = inspect(conexion)
    for tabla, columnas in COLUMNAS_AGREGADAS.items():
        if not inspector.has_table(tabla):
            continue
        existentes = {c["name"] for c in inspector.get_columns(tabla)}
        for nombre, tipo in columnas.items():
            if nombre not in existentes:
                conexion.exec_driver_sql(f"ALTER TABLE {tabla} ADD COLUMN {nombre} {tipo}")


def asegurar_valores(conexion: Connection, base: EsquemaBase) -> None:
    for tabla, valor in VALORES_AGREGADOS.items():
        sql = conexion.execute(
            text("SELECT sql FROM sqlite_master WHERE type = 'table' AND name = :t"),
            {"t": tabla},
        ).scalar()
        if not sql or "CHECK" not in sql or valor in sql:
            continue
        indices = conexion.execute(
            text(
                "SELECT name FROM sqlite_master WHERE type = 'index' AND tbl_name = :t "
                "AND name NOT LIKE 'sqlite_autoindex%'"
            ),
            {"t": tabla},
        ).scalars()
        for indice in list(indices):
            conexion.exec_driver_sql(f'DROP INDEX "{indice}"')
        conexion.exec_driver_sql(f'ALTER TABLE "{tabla}" RENAME TO "{tabla}_anterior"')
        conexion.exec_driver_sql(base.tablas[tabla])
        columnas = ", ".join(f'"{c.name}"' for c in base.metadata.tables[tabla].columns)
        conexion.exec_driver_sql(
            f'INSERT INTO "{tabla}" ({columnas}) SELECT {columnas} FROM "{tabla}_anterior"'
        )
        conexion.exec_driver_sql(f'DROP TABLE "{tabla}_anterior"')


def _indices_de(conexion: Connection, tabla: str, columna: str) -> list[str]:
    indices = conexion.exec_driver_sql(f'PRAGMA index_list("{tabla}")').mappings().all()
    return [
        indice["name"]
        for indice in indices
        if indice["origin"] == "c"
        and [
            fila["name"]
            for fila in conexion.exec_driver_sql(
                f'PRAGMA index_info("{indice["name"]}")'
            ).mappings()
        ]
        == [columna]
    ]


def renombrar_sub(conexion: Connection) -> None:
    inspector = inspect(conexion)
    if not inspector.has_table("usuarios"):
        return
    existentes = [c["name"] for c in inspector.get_columns("usuarios")]
    if COLUMNA_SUB in existentes:
        return
    anterior = next((c for c in existentes if c.endswith(SUFIJO_SUB_ANTERIOR)), None)
    if anterior is None:
        return
    conexion.exec_driver_sql(f'ALTER TABLE usuarios RENAME COLUMN "{anterior}" TO "{COLUMNA_SUB}"')
    for indice in _indices_de(conexion, "usuarios", COLUMNA_SUB):
        conexion.exec_driver_sql(f'DROP INDEX "{indice}"')
    conexion.exec_driver_sql(
        f'CREATE UNIQUE INDEX "ix_usuarios_{COLUMNA_SUB}" ON usuarios ("{COLUMNA_SUB}")'
    )
