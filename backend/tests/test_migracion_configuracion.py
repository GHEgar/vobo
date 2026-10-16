from pathlib import Path

from alembic import command
from sqlalchemy import create_engine, inspect

from app import inicializar
from app.core import migraciones
from tests.apoyo_migraciones import conserva, volcado

DATOS_0003 = """
INSERT INTO rondas VALUES (1, 'Ronda 1', 's1', 1, '2026-01-01 00:00:00');
INSERT INTO usuarios VALUES
    (1, 'sub-ana', 'ana@ejemplo.test', 'Ana', '2026-01-01 00:00:00', '["validacion.admin"]');
INSERT INTO resultados VALUES
    (1, 1, 'A-GEN-01', 'ana@ejemplo.test', 'pasa', '[1]', 'bien', '2026-01-01 01:00:00');
INSERT INTO contenido_secciones VALUES
    ('s1', 0, '{"id": "s1", "sistema": "general"}', '2026-01-01 00:00:00', 'ana@ejemplo.test');
"""


def _base_en_0003(tmp_path: Path):
    motor = create_engine(f"sqlite:///{tmp_path / 'base.sqlite3'}")
    transaccional = migraciones.motor_transaccional(motor.url)
    with transaccional.begin() as conexion:
        command.upgrade(migraciones.configuracion(conexion), "0003")
        for sentencia in DATOS_0003.split(";"):
            if sentencia.strip():
                conexion.exec_driver_sql(sentencia)
    transaccional.dispose()
    return motor


def test_0004_sobre_0003_conserva_datos_y_crea_la_tabla_vacia(tmp_path, monkeypatch) -> None:
    motor = _base_en_0003(tmp_path)
    antes = volcado(motor)
    monkeypatch.setattr(inicializar, "engine", motor)
    inicializar.preparar_base()
    despues = volcado(motor)
    assert migraciones.revision_actual(motor) == migraciones.revision_head()
    assert set(despues) == set(antes) | {"configuracion", "proyectos"}
    assert conserva(antes, despues)
    assert despues["configuracion"] == []
    motor.dispose()


def test_0004_baja_y_sube_sin_perder_lo_anterior(tmp_path) -> None:
    motor = _base_en_0003(tmp_path)
    antes = volcado(motor)
    transaccional = migraciones.motor_transaccional(motor.url)
    with transaccional.begin() as conexion:
        command.upgrade(migraciones.configuracion(conexion), "0004")
        command.downgrade(migraciones.configuracion(conexion), "0003")
        assert "configuracion" not in inspect(conexion).get_table_names()
        command.upgrade(migraciones.configuracion(conexion), "head")
    transaccional.dispose()
    assert conserva(antes, volcado(motor))
    motor.dispose()
