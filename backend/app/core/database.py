from collections.abc import Generator
from pathlib import Path
from sqlite3 import Connection

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.engine import Connection as Conexion
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.pool import ConnectionPoolEntry

from app.core.config import settings

Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    f"sqlite:///{settings.database_path}",
    connect_args={"check_same_thread": False, "timeout": 15},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@event.listens_for(engine, "connect")
def _pragmas(conexion: Connection, _registro: ConnectionPoolEntry) -> None:
    cursor = conexion.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


COLUMNAS_AGREGADAS = {
    "resultados": {"comentario": "TEXT"},
    "usuarios": {"permisos": "JSON"},
    "fallas": {"seccion_id": "VARCHAR(120)", "tipo": "VARCHAR(10) NOT NULL DEFAULT 'falla'"},
}


def asegurar_columnas() -> None:
    inspector = inspect(engine)
    with engine.begin() as conexion:
        for tabla, columnas in COLUMNAS_AGREGADAS.items():
            if not inspector.has_table(tabla):
                continue
            existentes = {c["name"] for c in inspector.get_columns(tabla)}
            for nombre, tipo in columnas.items():
                if nombre not in existentes:
                    conexion.execute(text(f"ALTER TABLE {tabla} ADD COLUMN {nombre} {tipo}"))


VALORES_AGREGADOS = {"decisiones": "desplegar_con_aviso"}


def asegurar_valores() -> None:
    with engine.begin() as conexion:
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
                conexion.execute(text(f'DROP INDEX "{indice}"'))
            conexion.execute(text(f'ALTER TABLE "{tabla}" RENAME TO "{tabla}_anterior"'))
            definicion = Base.metadata.tables[tabla]
            definicion.create(conexion)
            columnas = ", ".join(f'"{c.name}"' for c in definicion.columns)
            conexion.execute(
                text(
                    f'INSERT INTO "{tabla}" ({columnas}) SELECT {columnas} FROM "{tabla}_anterior"'
                )
            )
            conexion.execute(text(f'DROP TABLE "{tabla}_anterior"'))


COLUMNA_SUB = "sub_oidc"
SUFIJO_SUB_ANTERIOR = "_sub"


def _indices_de(conexion: Conexion, tabla: str, columna: str) -> list[str]:
    indices = conexion.execute(text(f'PRAGMA index_list("{tabla}")')).mappings().all()
    return [
        indice["name"]
        for indice in indices
        if indice["origin"] == "c"
        and [
            fila["name"]
            for fila in conexion.execute(text(f'PRAGMA index_info("{indice["name"]}")')).mappings()
        ]
        == [columna]
    ]


def renombrar_sub() -> None:
    inspector = inspect(engine)
    if not inspector.has_table("usuarios"):
        return
    existentes = [c["name"] for c in inspector.get_columns("usuarios")]
    if COLUMNA_SUB in existentes:
        return
    anterior = next((c for c in existentes if c.endswith(SUFIJO_SUB_ANTERIOR)), None)
    if anterior is None:
        return
    with engine.begin() as conexion:
        conexion.execute(
            text(f'ALTER TABLE usuarios RENAME COLUMN "{anterior}" TO "{COLUMNA_SUB}"')
        )
        for indice in _indices_de(conexion, "usuarios", COLUMNA_SUB):
            conexion.execute(text(f'DROP INDEX "{indice}"'))
        conexion.execute(
            text(f'CREATE UNIQUE INDEX "ix_usuarios_{COLUMNA_SUB}" ON usuarios ("{COLUMNA_SUB}")')
        )
