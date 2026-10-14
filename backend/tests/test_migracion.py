import sqlite3
from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import Session

from app import inicializar
from app.core import database
from app.models.usuario import Sesion, Usuario

ANTERIOR = "proveedor_sub"

ESQUEMA_VIEJO = f"""
CREATE TABLE usuarios (
    id INTEGER NOT NULL,
    {ANTERIOR} VARCHAR(64),
    email VARCHAR(200) NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    ultimo_acceso DATETIME NOT NULL,
    permisos JSON,
    PRIMARY KEY (id)
);
CREATE INDEX ix_usuarios_id ON usuarios (id);
CREATE UNIQUE INDEX ix_usuarios_{ANTERIOR} ON usuarios ({ANTERIOR});
CREATE UNIQUE INDEX ix_usuarios_email ON usuarios (email);
CREATE TABLE sesiones (
    id VARCHAR(64) NOT NULL,
    usuario_id INTEGER NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    access_expira DATETIME NOT NULL,
    permisos_locales JSON,
    created_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
);
INSERT INTO usuarios VALUES
    (1, 'sub-ana', 'ana@ejemplo.test', 'Ana', '2026-01-01 00:00:00', '["a"]'),
    (2, NULL, 'beto@ejemplo.test', 'Beto', '2026-01-02 00:00:00', NULL);
INSERT INTO sesiones VALUES
    ('s1', 1, 'acceso', 'refresco', '2026-01-01 00:15:00', NULL, '2026-01-01 00:00:00');
"""


@pytest.fixture
def base_vieja(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    ruta = tmp_path / "vieja.sqlite3"
    with sqlite3.connect(ruta) as conexion:
        conexion.executescript(ESQUEMA_VIEJO)
    motor = create_engine(f"sqlite:///{ruta}")
    monkeypatch.setattr(database, "engine", motor)
    monkeypatch.setattr(inicializar, "engine", motor)
    yield motor
    motor.dispose()


def test_renombra_la_columna_y_conserva_datos(base_vieja) -> None:
    inicializar.preparar_base()
    inspector = inspect(base_vieja)
    columnas = [c["name"] for c in inspector.get_columns("usuarios")]
    assert "sub_oidc" in columnas
    assert ANTERIOR not in columnas
    indices = {i["name"]: i for i in inspector.get_indexes("usuarios")}
    assert indices["ix_usuarios_sub_oidc"]["unique"]
    assert indices["ix_usuarios_sub_oidc"]["column_names"] == ["sub_oidc"]
    assert f"ix_usuarios_{ANTERIOR}" not in indices
    with Session(base_vieja) as db:
        ana = db.scalar(select(Usuario).where(Usuario.sub_oidc == "sub-ana"))
        assert ana is not None
        assert (ana.email, ana.nombre, ana.permisos) == ("ana@ejemplo.test", "Ana", ["a"])
        assert db.get(Usuario, 2).sub_oidc is None
        assert db.get(Sesion, "s1").usuario_id == 1


def test_el_indice_sigue_siendo_unico(base_vieja) -> None:
    inicializar.preparar_base()
    with Session(base_vieja) as db:
        db.add(Usuario(sub_oidc="sub-ana", email="otra@ejemplo.test", nombre="Otra"))
        with pytest.raises(Exception, match="UNIQUE"):
            db.commit()


def test_es_idempotente(base_vieja) -> None:
    inicializar.preparar_base()
    inicializar.preparar_base()
    columnas = [c["name"] for c in inspect(base_vieja).get_columns("usuarios")]
    assert columnas.count("sub_oidc") == 1
