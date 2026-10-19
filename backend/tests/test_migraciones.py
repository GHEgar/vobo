import sqlite3
from collections.abc import Callable
from pathlib import Path

import pytest
from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import Engine, create_engine, inspect, select, text
from sqlalchemy.orm import Session

from app import inicializar
from app.core import migraciones
from app.core.adopcion import SUFIJO_SUB_ANTERIOR, checks_de
from app.core.database import Base
from app.models import Decision, Usuario

ANTERIOR = "proveedor" + SUFIJO_SUB_ANTERIOR

ESQUEMA_VIEJO = f"""
CREATE TABLE rondas (
    id INTEGER NOT NULL, nombre VARCHAR(120) NOT NULL, snapshot VARCHAR(200) NOT NULL,
    abierta BOOLEAN NOT NULL, creada DATETIME NOT NULL, PRIMARY KEY (id)
);
CREATE INDEX ix_rondas_id ON rondas (id);
CREATE TABLE usuarios (
    id INTEGER NOT NULL, {ANTERIOR} VARCHAR(64), email VARCHAR(200) NOT NULL,
    nombre VARCHAR(200) NOT NULL, ultimo_acceso DATETIME NOT NULL, PRIMARY KEY (id)
);
CREATE INDEX ix_usuarios_id ON usuarios (id);
CREATE UNIQUE INDEX ix_usuarios_{ANTERIOR} ON usuarios ({ANTERIOR});
CREATE UNIQUE INDEX ix_usuarios_email ON usuarios (email);
CREATE TABLE sesiones (
    id VARCHAR(64) NOT NULL, usuario_id INTEGER NOT NULL, access_token TEXT NOT NULL,
    refresh_token TEXT, access_expira DATETIME NOT NULL, permisos_locales JSON,
    created_at DATETIME NOT NULL, PRIMARY KEY (id),
    FOREIGN KEY(usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
);
CREATE INDEX ix_sesiones_usuario_id ON sesiones (usuario_id);
CREATE TABLE resultados (
    id INTEGER NOT NULL, ronda_id INTEGER NOT NULL, caso_id VARCHAR(60) NOT NULL,
    usuario_email VARCHAR(200) NOT NULL, estado VARCHAR(9) NOT NULL, pasos_marcados JSON NOT NULL,
    actualizado DATETIME NOT NULL, PRIMARY KEY (id), UNIQUE (ronda_id, caso_id, usuario_email),
    FOREIGN KEY(ronda_id) REFERENCES rondas (id) ON DELETE CASCADE,
    CONSTRAINT estado_resultado CHECK (estado IN ('pendiente', 'pasa', 'falla', 'no_pude'))
);
CREATE INDEX ix_resultados_usuario_email ON resultados (usuario_email);
CREATE INDEX ix_resultados_id ON resultados (id);
CREATE INDEX ix_resultados_caso_id ON resultados (caso_id);
CREATE INDEX ix_resultados_ronda_id ON resultados (ronda_id);
CREATE TABLE asignaciones (
    id INTEGER NOT NULL, ronda_id INTEGER NOT NULL, usuario_email VARCHAR(200) NOT NULL,
    seccion_id VARCHAR(120) NOT NULL, PRIMARY KEY (id),
    UNIQUE (ronda_id, usuario_email, seccion_id),
    FOREIGN KEY(ronda_id) REFERENCES rondas (id) ON DELETE CASCADE
);
CREATE INDEX ix_asignaciones_usuario_email ON asignaciones (usuario_email);
CREATE INDEX ix_asignaciones_id ON asignaciones (id);
CREATE INDEX ix_asignaciones_ronda_id ON asignaciones (ronda_id);
CREATE TABLE fallas (
    id INTEGER NOT NULL, ronda_id INTEGER NOT NULL, caso_id VARCHAR(60) NOT NULL,
    usuario_email VARCHAR(200) NOT NULL, paso INTEGER, obtenido TEXT NOT NULL,
    reproducible VARCHAR(7) NOT NULL, severidad VARCHAR(7) NOT NULL,
    navegador VARCHAR(400) NOT NULL, url VARCHAR(500) NOT NULL,
    version_visible VARCHAR(120) NOT NULL, creada DATETIME NOT NULL, estado VARCHAR(20) NOT NULL,
    nota_resolucion TEXT NOT NULL, PRIMARY KEY (id),
    FOREIGN KEY(ronda_id) REFERENCES rondas (id) ON DELETE CASCADE,
    CONSTRAINT reproducible CHECK (reproducible IN ('siempre', 'a_veces', 'una_vez')),
    CONSTRAINT severidad CHECK (severidad IN ('critica', 'alta', 'media', 'baja')),
    CONSTRAINT estado_falla CHECK (
        estado IN ('nueva', 'en_curso', 'lista_para_revalidar', 'cerrada')
    )
);
CREATE INDEX ix_fallas_severidad ON fallas (severidad);
CREATE INDEX ix_fallas_id ON fallas (id);
CREATE INDEX ix_fallas_caso_id ON fallas (caso_id);
CREATE INDEX ix_fallas_ronda_id ON fallas (ronda_id);
CREATE INDEX ix_fallas_usuario_email ON fallas (usuario_email);
CREATE INDEX ix_fallas_estado ON fallas (estado);
CREATE TABLE evidencias (
    id INTEGER NOT NULL, falla_id INTEGER NOT NULL, ruta VARCHAR(300) NOT NULL,
    mime VARCHAR(40) NOT NULL, creada DATETIME NOT NULL, PRIMARY KEY (id),
    FOREIGN KEY(falla_id) REFERENCES fallas (id) ON DELETE CASCADE
);
CREATE INDEX ix_evidencias_id ON evidencias (id);
CREATE INDEX ix_evidencias_falla_id ON evidencias (falla_id);
CREATE TABLE accesos (
    id INTEGER NOT NULL, usuario_email VARCHAR(200) NOT NULL, paginas JSON NOT NULL,
    actualizado DATETIME NOT NULL, PRIMARY KEY (id)
);
CREATE INDEX ix_accesos_id ON accesos (id);
CREATE UNIQUE INDEX ix_accesos_usuario_email ON accesos (usuario_email);
CREATE TABLE aprobaciones (
    id INTEGER NOT NULL, ronda_id INTEGER NOT NULL, tipo VARCHAR(14) NOT NULL,
    objetivo_id VARCHAR(120) NOT NULL, estado VARCHAR(9) NOT NULL, comentario TEXT NOT NULL,
    usuario_email VARCHAR(200) NOT NULL, usuario_nombre VARCHAR(200) NOT NULL,
    creada DATETIME NOT NULL, PRIMARY KEY (id),
    FOREIGN KEY(ronda_id) REFERENCES rondas (id) ON DELETE CASCADE,
    CONSTRAINT tipo_aprobacion CHECK (tipo IN ('herramienta', 'caracteristica')),
    CONSTRAINT estado_aprobacion CHECK (estado IN ('aprobada', 'rechazada', 'pendiente'))
);
CREATE INDEX ix_aprobaciones_objetivo_id ON aprobaciones (objetivo_id);
CREATE INDEX ix_aprobaciones_ronda_id ON aprobaciones (ronda_id);
CREATE INDEX ix_aprobaciones_id ON aprobaciones (id);
CREATE TABLE decisiones (
    id INTEGER NOT NULL, ronda_id INTEGER NOT NULL, herramienta_id VARCHAR(120) NOT NULL,
    decision VARCHAR(9) NOT NULL, motivo TEXT NOT NULL, decidido_por VARCHAR(200) NOT NULL,
    actualizado DATETIME NOT NULL, PRIMARY KEY (id), UNIQUE (ronda_id, herramienta_id),
    FOREIGN KEY(ronda_id) REFERENCES rondas (id) ON DELETE CASCADE,
    CONSTRAINT decision CHECK (decision IN ('desplegar', 'aplazar', 'pendiente'))
);
CREATE INDEX ix_decisiones_ronda_id ON decisiones (ronda_id);
CREATE INDEX ix_decisiones_id ON decisiones (id);
CREATE INDEX ix_decisiones_herramienta_id ON decisiones (herramienta_id);
INSERT INTO rondas VALUES (1, 'Ronda 1', 's1', 1, '2026-01-01 00:00:00');
INSERT INTO usuarios VALUES
    (1, 'sub-ana', 'ana@ejemplo.test', 'Ana', '2026-01-01 00:00:00'),
    (2, NULL, 'beto@ejemplo.test', 'Beto', '2026-01-02 00:00:00');
INSERT INTO sesiones VALUES
    ('s1', 1, 'acceso', 'refresco', '2026-01-01 00:15:00', NULL, '2026-01-01 00:00:00');
INSERT INTO resultados VALUES
    (1, 1, 'c1', 'ana@ejemplo.test', 'pasa', '[1, 2]', '2026-01-01 01:00:00'),
    (2, 1, 'c2', 'beto@ejemplo.test', 'falla', '[]', '2026-01-01 02:00:00');
INSERT INTO asignaciones VALUES (1, 1, 'ana@ejemplo.test', 'sec-a');
INSERT INTO fallas VALUES
    (1, 1, 'c2', 'beto@ejemplo.test', 3, 'no carga', 'siempre', 'alta', 'nav', '/x', 'v1',
     '2026-01-01 02:00:00', 'nueva', '');
INSERT INTO evidencias VALUES (1, 1, 'f1.png', 'image/png', '2026-01-01 02:00:00');
INSERT INTO accesos VALUES (1, 'ana@ejemplo.test', '["tablero"]', '2026-01-01 00:00:00');
INSERT INTO aprobaciones VALUES
    (1, 1, 'herramienta', 'h1', 'aprobada', 'ok', 'ana@ejemplo.test', 'Ana', '2026-01-03 00:00:00');
INSERT INTO decisiones VALUES (1, 1, 'h1', 'aplazar', 'falta', 'Ana', '2026-01-03 00:00:00');
"""
RENOMBRES = {("usuarios", ANTERIOR): "sub_oidc"}
NUEVAS = {
    "avisos",
    "presencias",
    "roles",
    "usuario_roles",
    "cuentas",
    "invitaciones",
    "restablecimientos",
    "intentos_entrada",
    "contenido_secciones",
    "contenido_procedimientos",
    "contenido_versiones",
    "contenido_media",
    "configuracion",
    "proyectos",
    "resultados_historial",
    "comentarios_seguimiento",
    "seguimiento",
}


@pytest.fixture
def motor_de(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    motores: list[Engine] = []

    def crear(script: str = "") -> Engine:
        ruta = tmp_path / f"base-{len(motores)}.sqlite3"
        with sqlite3.connect(ruta) as conexion:
            conexion.executescript(script)
        motor = create_engine(f"sqlite:///{ruta}")
        motores.append(motor)
        monkeypatch.setattr(inicializar, "engine", motor)
        return motor

    yield crear
    for motor in motores:
        motor.dispose()


def _datos(motor: Engine) -> dict[str, list[dict]]:
    with motor.connect() as conexion:
        tablas = [t for t in inspect(conexion).get_table_names() if t != "alembic_version"]
        return {
            tabla: [
                dict(f)
                for f in conexion.execute(text(f'SELECT * FROM "{tabla}" ORDER BY 1')).mappings()
            ]
            for tabla in tablas
        }


def _sin_diferencias(motor: Engine) -> None:
    with motor.connect() as conexion:
        contexto = MigrationContext.configure(conexion, opts={"compare_type": True})
        assert compare_metadata(contexto, Base.metadata) == []
        base = migraciones.esquema_base()
        assert checks_de(conexion, list(base.checks)) == base.checks
    assert migraciones.revision_actual(motor) == migraciones.revision_head()


def test_base_vacia_queda_en_head_igual_a_los_modelos(motor_de: Callable[..., Engine]) -> None:
    motor = motor_de()
    inicializar.preparar_base()
    _sin_diferencias(motor)
    assert set(inspect(motor).get_table_names()) == set(Base.metadata.tables) | {"alembic_version"}


def test_adopta_la_base_vieja_sin_perder_datos(motor_de: Callable[..., Engine]) -> None:
    motor = motor_de(ESQUEMA_VIEJO)
    antes = _datos(motor)
    inicializar.preparar_base()
    _sin_diferencias(motor)
    assert migraciones.revision_actual(motor) == migraciones.revision_head()
    despues = _datos(motor)
    assert set(despues) == set(antes) | NUEVAS
    assert all(despues[t] == [] for t in NUEVAS - {"roles", "proyectos"})
    assert len(despues["roles"]) == 6
    assert [p["clave"] for p in despues["proyectos"]] == ["principal"]
    assert {r["proyecto_id"] for r in despues["rondas"]} == {despues["proyectos"][0]["id"]}
    for tabla, filas in antes.items():
        assert len(despues[tabla]) == len(filas)
        for vieja, nueva in zip(filas, despues[tabla], strict=True):
            for columna, valor in vieja.items():
                assert nueva[RENOMBRES.get((tabla, columna), columna)] == valor


def test_la_base_adoptada_acepta_los_valores_nuevos(motor_de: Callable[..., Engine]) -> None:
    motor = motor_de(ESQUEMA_VIEJO)
    inicializar.preparar_base()
    with Session(motor) as db:
        assert db.scalar(select(Usuario).where(Usuario.sub_oidc == "sub-ana")).nombre == "Ana"
        db.get(Decision, 1).decision = "desplegar_con_aviso"
        db.commit()
        db.add(Usuario(sub_oidc="sub-ana", email="otra@ejemplo.test", nombre="Otra"))
        with pytest.raises(Exception, match="UNIQUE"):
            db.commit()


@pytest.mark.parametrize("script", ["", ESQUEMA_VIEJO], ids=["vacia", "vieja"])
def test_es_idempotente(motor_de: Callable[..., Engine], script: str) -> None:
    motor = motor_de(script)
    inicializar.preparar_base()
    antes = _datos(motor)
    inicializar.preparar_base()
    assert _datos(motor) == antes
    _sin_diferencias(motor)


def test_aborta_sin_tocar_nada_si_el_esquema_no_coincide(motor_de: Callable[..., Engine]) -> None:
    motor = motor_de(ESQUEMA_VIEJO + "CREATE TABLE ajena (id INTEGER PRIMARY KEY);")
    with motor.connect() as conexion:
        esquema = conexion.execute(text("SELECT * FROM sqlite_master ORDER BY name")).all()
    antes = _datos(motor)
    with pytest.raises(migraciones.EsquemaIncompatible, match="ajena"):
        inicializar.preparar_base()
    with motor.connect() as conexion:
        assert conexion.execute(text("SELECT * FROM sqlite_master ORDER BY name")).all() == esquema
    assert _datos(motor) == antes
