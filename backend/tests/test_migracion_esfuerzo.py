import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError

from app.core import migraciones
from tests.apoyo_migraciones import conserva, volcado
from tests.test_migracion_presencia import _bajar, _migrar
from tests.test_migracion_quitar_pantallas import _base_en_0009

DATOS_0010 = """
INSERT INTO seguimiento (objeto, objeto_id, autor_email, accion, texto, anterior, nuevo, creado)
VALUES ('falla', 1, 'ana@ejemplo.test', 'estado', '', 'nueva', 'en_curso', '2026-10-18 10:00:00');
INSERT INTO seguimiento (objeto, objeto_id, autor_email, accion, texto, anterior, nuevo, creado)
VALUES ('comentario', 1, 'ana@ejemplo.test', 'respuesta', 'Hola', NULL, NULL,
    '2026-10-18 11:00:00')
"""
NUEVAS = {"esfuerzo_horas", "principal_objeto", "principal_id"}
TABLAS = ("fallas", "comentarios_seguimiento")
VINCULO = (
    "INSERT INTO seguimiento (objeto, objeto_id, autor_email, accion, texto, creado) "
    "VALUES ('falla', 1, 'ana@ejemplo.test', 'vinculo', '', '2026-10-19 10:00:00')"
)


def _esquema(motor, tabla: str) -> str:
    with motor.connect() as conexion:
        consulta = text("SELECT sql FROM sqlite_master WHERE type = 'table' AND name = :t")
        return conexion.execute(consulta, {"t": tabla}).scalar_one()


def _checks(motor) -> dict[str, int]:
    return {t: _esquema(motor, t).count("CHECK") for t in (*TABLAS, "seguimiento")}


def _base_en_0010(tmp_path):
    motor = _base_en_0009(tmp_path)
    _migrar(motor, "0010", DATOS_0010)
    return motor


def test_0011_agrega_columnas_y_acciones_sin_perder_datos(tmp_path) -> None:
    motor = _base_en_0010(tmp_path)
    antes = volcado(motor)
    checks = _checks(motor)
    assert antes["fallas"] and antes["comentarios_seguimiento"] and len(antes["seguimiento"]) == 2
    _migrar(motor, "0011")
    despues = volcado(motor)
    assert set(despues) == set(antes)
    assert conserva(antes, despues)
    assert _checks(motor) == checks
    assert checks["fallas"] > 0 and checks["seguimiento"] == 2
    assert "'vinculo'" in _esquema(motor, "seguimiento")
    with motor.connect() as conexion:
        inspector = inspect(conexion)
        for tabla in TABLAS:
            assert NUEVAS <= {c["name"] for c in inspector.get_columns(tabla)}
            assert f"ix_{tabla}_principal" in {i["name"] for i in inspector.get_indexes(tabla)}
        assert "ix_seguimiento_objeto" in {i["name"] for i in inspector.get_indexes("seguimiento")}
    assert all(f[c] is None for t in TABLAS for f in despues[t] for c in NUEVAS)
    with motor.begin() as conexion:
        conexion.exec_driver_sql(VINCULO)
    assert migraciones.revision_actual(motor) == migraciones.revision_head() == "0011"
    motor.dispose()


def test_baja_a_0010_y_vuelve(tmp_path) -> None:
    motor = _base_en_0010(tmp_path)
    antes = volcado(motor)
    checks = _checks(motor)
    _migrar(motor, "0011")
    with motor.begin() as conexion:
        conexion.exec_driver_sql(VINCULO)
        conexion.exec_driver_sql("UPDATE fallas SET esfuerzo_horas = 6")
    _bajar(motor, "0010")
    assert volcado(motor) == antes
    assert _checks(motor) == checks
    with pytest.raises(IntegrityError), motor.begin() as conexion:
        conexion.exec_driver_sql(VINCULO)
    _migrar(motor, "head")
    assert conserva(antes, volcado(motor))
    assert migraciones.revision_actual(motor) == "0011"
    motor.dispose()
