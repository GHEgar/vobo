from pathlib import Path

import pytest
from alembic import command
from sqlalchemy import create_engine, inspect

from app import inicializar
from app.core import migraciones
from app.core.config import settings
from tests.apoyo_migraciones import conserva, volcado

DATOS_0004 = """
INSERT INTO rondas VALUES (1, 'Ronda 1', 's1', 1, '2026-01-01 00:00:00');
INSERT INTO rondas VALUES (2, 'Ronda 2', 's2', 0, '2026-02-01 00:00:00');
INSERT INTO resultados VALUES
    (1, 1, 'A-GEN-01', 'ana@ejemplo.test', 'pasa', '[1]', 'bien', '2026-01-01 01:00:00');
INSERT INTO asignaciones VALUES (1, 1, 'ana@ejemplo.test', 's1');
INSERT INTO fallas VALUES
    (1, 1, 'A-GEN-01', 'ana@ejemplo.test', 0, NULL, 'falla', 'no carga', 'siempre', 'alta',
     'nav', '/x', 'v1', '2026-01-01 02:00:00', 'nueva', '');
INSERT INTO avisos VALUES
    (1, 'ana@ejemplo.test', 'Hola', 'Atendida', 1, 'A-GEN-01', 'b@x.test', 'B',
     '2026-01-02 00:00:00', NULL);
INSERT INTO presencias VALUES
    ('ana@ejemplo.test', 'Ana', '/', NULL, NULL, NULL, 'viendo', 1, '2026-01-02 00:00:00');
INSERT INTO contenido_secciones VALUES
    ('s1', 10, '{"id": "s1", "sistema": "general"}', '2026-01-01 00:00:00', 'ana@ejemplo.test');
INSERT INTO contenido_procedimientos VALUES
    ('p1', 1, '{"id": "p1", "pasos": []}', '2026-01-01 00:00:00', 'ana@ejemplo.test');
INSERT INTO contenido_media VALUES
    ('p1', 'p1.webp', 'image/webp', 10, 'abc', '2026-01-01 00:00:00', 'ana@ejemplo.test');
INSERT INTO contenido_versiones VALUES
    (1, 'seccion', 's1', 'crear', NULL, 'ana@ejemplo.test', '2026-01-01 00:00:00');
"""
CON_PROYECTO = (
    "rondas",
    "contenido_secciones",
    "contenido_procedimientos",
    "contenido_media",
    "contenido_versiones",
    "avisos",
    "presencias",
)


def _base_en_0004(tmp_path: Path, extra: str = ""):
    motor = create_engine(f"sqlite:///{tmp_path / 'base.sqlite3'}")
    transaccional = migraciones.motor_transaccional(motor.url)
    with transaccional.begin() as conexion:
        command.upgrade(migraciones.configuracion(conexion), "0004")
        for sentencia in (DATOS_0004 + extra).split(";"):
            if sentencia.strip():
                conexion.exec_driver_sql(sentencia)
    transaccional.dispose()
    return motor


@pytest.fixture
def subir(monkeypatch: pytest.MonkeyPatch):
    def aplicar(motor) -> dict[str, list[dict]]:
        monkeypatch.setattr(inicializar, "engine", motor)
        inicializar.preparar_base()
        return volcado(motor)

    return aplicar


def test_todo_queda_en_el_proyecto_por_omision(tmp_path, subir) -> None:
    motor = _base_en_0004(tmp_path)
    antes = volcado(motor)
    despues = subir(motor)
    assert migraciones.revision_actual(motor) == migraciones.revision_head()
    assert set(despues) == set(antes) | {"proyectos"}
    assert conserva(antes, despues)
    [proyecto] = despues["proyectos"]
    assert proyecto["clave"] == "principal"
    assert proyecto["por_omision"] and not proyecto["archivado"]
    for tabla in CON_PROYECTO:
        assert {f["proyecto_id"] for f in despues[tabla]} == {proyecto["id"]}, tabla
    with motor.connect() as conexion:
        claves = inspect(conexion).get_pk_constraint("contenido_secciones")["constrained_columns"]
    assert claves == ["proyecto_id", "id"]
    motor.dispose()


def test_el_nombre_viene_de_la_configuracion_guardada(tmp_path, subir) -> None:
    guardado = "INSERT INTO configuracion VALUES ('nombre', '\"Release 2.0\"', '2026-01-01', 'a');"
    motor = _base_en_0004(tmp_path, guardado)
    assert subir(motor)["proyectos"][0]["nombre"] == "Release 2.0"
    motor.dispose()


def test_sin_configuracion_usa_el_nombre_de_los_archivos(tmp_path, subir) -> None:
    motor = _base_en_0004(tmp_path)
    assert subir(motor)["proyectos"][0]["nombre"] == "Tienda en línea"
    motor.dispose()


def test_sin_nombre_queda_principal(tmp_path, subir, monkeypatch) -> None:
    monkeypatch.setattr(settings, "contenido_dir", str(tmp_path / "no-existe"))
    motor = _base_en_0004(tmp_path)
    assert subir(motor)["proyectos"][0]["nombre"] == "Principal"
    motor.dispose()


def test_baja_y_sube_sin_perder_lo_anterior(tmp_path) -> None:
    motor = _base_en_0004(tmp_path)
    antes = volcado(motor)
    transaccional = migraciones.motor_transaccional(motor.url)
    with transaccional.begin() as conexion:
        command.upgrade(migraciones.configuracion(conexion), "0005")
        command.downgrade(migraciones.configuracion(conexion), "0004")
        assert "proyectos" not in inspect(conexion).get_table_names()
    transaccional.dispose()
    assert volcado(motor) == antes
    transaccional = migraciones.motor_transaccional(motor.url)
    with transaccional.begin() as conexion:
        command.upgrade(migraciones.configuracion(conexion), "head")
    transaccional.dispose()
    assert conserva(antes, volcado(motor))
    motor.dispose()
