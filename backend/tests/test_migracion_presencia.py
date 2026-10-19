from alembic import command
from sqlalchemy import create_engine, inspect

from app.core import migraciones
from tests.apoyo_migraciones import conserva, volcado
from tests.test_migracion_proyectos import DATOS_0004

NUEVAS = {"navegador", "agente", "dispositivo", "pantalla", "desde"}


def _migrar(motor, revision: str, datos: str = "") -> None:
    transaccional = migraciones.motor_transaccional(motor.url)
    with transaccional.begin() as conexion:
        command.upgrade(migraciones.configuracion(conexion), revision)
        for sentencia in datos.split(";"):
            if sentencia.strip():
                conexion.exec_driver_sql(sentencia)
    transaccional.dispose()


def _bajar(motor, revision: str) -> None:
    transaccional = migraciones.motor_transaccional(motor.url)
    with transaccional.begin() as conexion:
        command.downgrade(migraciones.configuracion(conexion), revision)
    transaccional.dispose()


def _base_en_0005(tmp_path):
    motor = create_engine(f"sqlite:///{tmp_path / 'base.sqlite3'}")
    _migrar(motor, "0004", DATOS_0004)
    _migrar(motor, "0005")
    return motor


def test_presencias_ganan_metadatos_sin_perder_datos(tmp_path) -> None:
    motor = _base_en_0005(tmp_path)
    antes = volcado(motor)
    _migrar(motor, "0006")
    despues = volcado(motor)
    assert conserva(antes, despues)
    [fila] = despues["presencias"]
    assert fila["navegador"] == "" and fila["agente"] == ""
    assert fila["dispositivo"] == "escritorio"
    assert fila["pantalla"] is None
    assert fila["desde"] == fila["actualizado"]
    with motor.connect() as conexion:
        columnas = {c["name"] for c in inspect(conexion).get_columns("presencias")}
    assert NUEVAS <= columnas
    motor.dispose()


def test_baja_a_0005_y_vuelve(tmp_path) -> None:
    motor = _base_en_0005(tmp_path)
    antes = volcado(motor)
    _migrar(motor, "0006")
    _bajar(motor, "0005")
    assert volcado(motor) == antes
    _migrar(motor, "head")
    assert conserva(antes, volcado(motor))
    assert migraciones.revision_actual(motor) == migraciones.revision_head() == "0010"
    motor.dispose()
