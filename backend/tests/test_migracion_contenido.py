from pathlib import Path

from alembic import command
from sqlalchemy import create_engine, inspect, text

from app import inicializar
from app.core import migraciones
from app.core.config import settings
from tests.apoyo_migraciones import conserva, volcado

DATOS_0002 = """
INSERT INTO rondas VALUES (1, 'Ronda 1', 's1', 1, '2026-01-01 00:00:00');
INSERT INTO usuarios VALUES
    (1, 'sub-ana', 'ana@ejemplo.test', 'Ana', '2026-01-01 00:00:00', '["validacion.admin"]');
INSERT INTO resultados VALUES
    (1, 1, 'A-GEN-01', 'ana@ejemplo.test', 'pasa', '[1]', 'bien', '2026-01-01 01:00:00');
INSERT INTO usuario_roles VALUES (1, 4);
"""

NUEVAS = {
    "contenido_secciones",
    "contenido_procedimientos",
    "contenido_versiones",
    "contenido_media",
    "configuracion",
}


def _base_en_0002(tmp_path: Path):
    motor = create_engine(f"sqlite:///{tmp_path / 'base.sqlite3'}")
    transaccional = migraciones.motor_transaccional(motor.url)
    with transaccional.begin() as conexion:
        command.upgrade(migraciones.configuracion(conexion), "0002")
        for sentencia in DATOS_0002.split(";"):
            if sentencia.strip():
                conexion.exec_driver_sql(sentencia)
    transaccional.dispose()
    return motor


def _volcado(motor) -> dict[str, list]:
    with motor.connect() as conexion:
        tablas = [t for t in inspect(conexion).get_table_names() if t != "alembic_version"]
        return {t: conexion.execute(text(f'SELECT * FROM "{t}" ORDER BY 1')).all() for t in tablas}


def test_0003_sobre_0002_conserva_datos_y_con_archivos_no_importa(tmp_path, monkeypatch) -> None:
    motor = _base_en_0002(tmp_path)
    antes = volcado(motor)
    monkeypatch.setattr(inicializar, "engine", motor)
    inicializar.preparar_base()
    despues = volcado(motor)
    assert migraciones.revision_actual(motor) == migraciones.revision_head()
    assert set(despues) == set(antes) | NUEVAS | {"proyectos"}
    assert conserva(antes, despues)
    assert all(despues[t] == [] for t in NUEVAS)
    motor.dispose()


def test_0003_con_base_importa_el_contenido_al_arrancar(tmp_path, monkeypatch) -> None:
    motor = _base_en_0002(tmp_path)
    monkeypatch.setattr(settings, "contenido_fuente", "base")
    monkeypatch.setattr(settings, "media_dir", str(tmp_path / "media"))
    monkeypatch.setattr(inicializar, "engine", motor)
    inicializar.preparar_base()
    inicializar.preparar_base()
    despues = _volcado(motor)
    assert len(despues["contenido_secciones"]) == 4
    assert len(despues["contenido_procedimientos"]) == 6
    assert len(despues["contenido_versiones"]) == 10
    assert len(despues["resultados"]) == 1
    motor.dispose()


def test_la_migracion_baja_y_sube_sin_perder_lo_anterior(tmp_path) -> None:
    motor = _base_en_0002(tmp_path)
    transaccional = migraciones.motor_transaccional(motor.url)
    with transaccional.begin() as conexion:
        command.upgrade(migraciones.configuracion(conexion), "0003")
        command.downgrade(migraciones.configuracion(conexion), "0002")
        assert not NUEVAS & set(inspect(conexion).get_table_names())
        command.upgrade(migraciones.configuracion(conexion), "head")
    transaccional.dispose()
    assert len(_volcado(motor)["resultados"]) == 1
    motor.dispose()
