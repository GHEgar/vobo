from sqlalchemy import inspect

from app.core import migraciones
from tests.apoyo_migraciones import conserva, volcado
from tests.test_migracion_historial import _base_en_0006
from tests.test_migracion_presencia import _bajar, _migrar

DATOS_0007 = (
    "INSERT INTO resultados_historial (ronda_id, caso_id, usuario_email, estado, accion, creado) "
    "SELECT id, 'A-GEN-01', 'ana@x.test', 'pasa', 'marcar', '2026-10-01 10:00:00' FROM rondas"
)


def _base_en_0007(tmp_path):
    motor = _base_en_0006(tmp_path)
    _migrar(motor, "0007", DATOS_0007)
    return motor


def test_0008_crea_pantallas_vacia_y_conserva_datos(tmp_path) -> None:
    motor = _base_en_0007(tmp_path)
    antes = volcado(motor)
    assert antes["resultados_historial"] and antes["rondas"]
    _migrar(motor, "0008")
    despues = volcado(motor)
    assert set(despues) == set(antes) | {"pantallas"}
    assert conserva(antes, despues)
    assert despues["pantallas"] == []
    with motor.connect() as conexion:
        inspector = inspect(conexion)
        columnas = {c["name"] for c in inspector.get_columns("pantallas")}
        indices = {i["name"]: i["unique"] for i in inspector.get_indexes("pantallas")}
    assert columnas == {
        "id",
        "nombre",
        "token_hash",
        "vistas",
        "segundos",
        "proyectos",
        "activa",
        "creada",
        "ultimo_uso",
        "autor_email",
    }
    assert indices == {"ix_pantallas_token_hash": 1}
    motor.dispose()


def test_baja_a_0007_y_vuelve(tmp_path) -> None:
    motor = _base_en_0007(tmp_path)
    antes = volcado(motor)
    _migrar(motor, "0008")
    _bajar(motor, "0007")
    assert volcado(motor) == antes
    _migrar(motor, "head")
    assert conserva(antes, volcado(motor))
    assert migraciones.revision_actual(motor) == migraciones.revision_head() == "0008"
    motor.dispose()
