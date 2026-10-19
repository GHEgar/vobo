from sqlalchemy import inspect, text

from app.core import migraciones
from tests.apoyo_migraciones import conserva, volcado
from tests.test_migracion_presencia import _bajar, _migrar
from tests.test_migracion_seguimiento import _base_en_0008


def _tablas(motor) -> set[str]:
    with motor.connect() as conexion:
        return set(inspect(conexion).get_table_names())


def _base_en_0009(tmp_path):
    motor = _base_en_0008(tmp_path)
    _migrar(motor, "0009")
    with motor.begin() as conexion:
        conexion.execute(
            text(
                "INSERT INTO pantallas (nombre, token_hash, vistas, segundos, proyectos, activa,"
                " creada, autor_email) VALUES ('Sala', 'h', '[]', 20, '[]', 1,"
                " '2026-10-18 10:00:00', 'ana@x.test')"
            )
        )
    return motor


def test_0010_quita_pantallas_y_conserva_lo_demas(tmp_path) -> None:
    motor = _base_en_0009(tmp_path)
    antes = volcado(motor)
    _migrar(motor, "0010")
    assert "pantallas" not in _tablas(motor)
    despues = volcado(motor)
    assert conserva({k: v for k, v in antes.items() if k != "pantallas"}, despues)
    assert migraciones.revision_actual(motor) == "0010"
    motor.dispose()


def test_baja_a_0009_y_vuelve(tmp_path) -> None:
    motor = _base_en_0009(tmp_path)
    _migrar(motor, "0010")
    _bajar(motor, "0009")
    assert "pantallas" in _tablas(motor)
    _migrar(motor, "head")
    assert "pantallas" not in _tablas(motor)
    motor.dispose()
