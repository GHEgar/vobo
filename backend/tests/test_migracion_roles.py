import importlib.util
from pathlib import Path

from alembic import command
from sqlalchemy import create_engine, inspect, text

from app import inicializar
from app.core import migraciones
from app.services import roles

DATOS_0001 = """
INSERT INTO rondas VALUES (1, 'Ronda 1', 's1', 1, '2026-01-01 00:00:00');
INSERT INTO usuarios VALUES
    (1, 'sub-ana', 'ana@ejemplo.test', 'Ana', '2026-01-01 00:00:00',
     '["validacion.casos.ejecutar"]'),
    (2, NULL, 'beto@ejemplo.test', 'Beto', '2026-01-02 00:00:00', NULL);
INSERT INTO sesiones VALUES
    ('s-oidc', 1, 'acceso', 'refresco', '2026-01-01 00:15:00', NULL, NULL, '2026-01-01 00:00:00'),
    ('s-local', 2, 'local', NULL, '2026-01-01 00:15:00', '["validacion.casos.ejecutar"]', NULL,
     '2026-01-01 00:00:00');
INSERT INTO resultados VALUES
    (1, 1, 'c1', 'ana@ejemplo.test', 'pasa', '[1, 2]', 'bien', '2026-01-01 01:00:00');
INSERT INTO accesos VALUES (1, 'ana@ejemplo.test', '["tablero"]', '2026-01-01 00:00:00');
"""


def _filas(conexion, tabla: str) -> list[dict]:
    filas = conexion.execute(text(f'SELECT * FROM "{tabla}" ORDER BY 1')).mappings()
    return [dict(f) for f in filas]


def test_0002_sobre_una_base_en_0001_conserva_los_datos(tmp_path: Path, monkeypatch) -> None:
    motor = create_engine(f"sqlite:///{tmp_path / 'base.sqlite3'}")
    transaccional = migraciones.motor_transaccional(motor.url)
    with transaccional.begin() as conexion:
        command.upgrade(migraciones.configuracion(conexion), "0001")
        for sentencia in DATOS_0001.split(";"):
            if sentencia.strip():
                conexion.exec_driver_sql(sentencia)
    transaccional.dispose()
    with motor.connect() as conexion:
        tablas = [t for t in inspect(conexion).get_table_names() if t != "alembic_version"]
        antes = {t: _filas(conexion, t) for t in tablas}

    monkeypatch.setattr(inicializar, "engine", motor)
    inicializar.preparar_base()

    assert migraciones.revision_actual(motor) == migraciones.revision_head()
    with motor.connect() as conexion:
        for tabla, filas in antes.items():
            despues = _filas(conexion, tabla)
            pares = zip(filas, despues, strict=True)
            assert [{k: f[k] for k in vieja} for vieja, f in pares] == filas
        origenes = dict(conexion.execute(text("SELECT id, origen FROM sesiones")).all())
        sembrados = _filas(conexion, "roles")
        assert _filas(conexion, "usuario_roles") == []
    motor.dispose()
    assert origenes == {"s-oidc": "oidc", "s-local": "local"}
    assert [{k: r[k] for k in ("clave", "nombre", "descripcion")} for r in sembrados] == [
        {k: r[k] for k in ("clave", "nombre", "descripcion")} for r in roles.ROLES_SISTEMA
    ]
    assert all(r["sistema"] == 1 for r in sembrados)


def test_la_siembra_de_la_migracion_coincide_con_la_app() -> None:
    ruta = next((migraciones.CARPETA_ALEMBIC / "versions").glob("0002_*.py"))
    especificacion = importlib.util.spec_from_file_location("revision_0002", ruta)
    modulo = importlib.util.module_from_spec(especificacion)
    especificacion.loader.exec_module(modulo)
    assert list(modulo.ROLES_SISTEMA) == list(roles.ROLES_SISTEMA)
