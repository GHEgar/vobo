from sqlalchemy import inspect

from app.core import migraciones
from tests.apoyo_migraciones import conserva, volcado
from tests.test_migracion_presencia import _bajar, _base_en_0005, _migrar


def _base_en_0006(tmp_path):
    motor = _base_en_0005(tmp_path)
    _migrar(motor, "0006")
    return motor


def test_historial_nace_vacio_y_las_rondas_cerradas_sin_fecha(tmp_path) -> None:
    motor = _base_en_0006(tmp_path)
    antes = volcado(motor)
    assert any(not r["abierta"] for r in antes["rondas"])
    _migrar(motor, "0007")
    despues = volcado(motor)
    assert conserva(antes, despues)
    assert despues["resultados_historial"] == []
    assert all(r["cerrada_en"] is None for r in despues["rondas"])
    assert despues["resultados"] == antes["resultados"]
    with motor.connect() as conexion:
        columnas = {c["name"] for c in inspect(conexion).get_columns("resultados_historial")}
    assert columnas == {
        "id",
        "ronda_id",
        "caso_id",
        "usuario_email",
        "estado",
        "paso",
        "accion",
        "creado",
    }
    motor.dispose()


def test_baja_a_0006_y_vuelve(tmp_path) -> None:
    motor = _base_en_0006(tmp_path)
    antes = volcado(motor)
    _migrar(motor, "0007")
    _bajar(motor, "0006")
    assert volcado(motor) == antes
    _migrar(motor, "head")
    assert conserva(antes, volcado(motor))
    assert migraciones.revision_actual(motor) == migraciones.revision_head() == "0008"
    motor.dispose()
