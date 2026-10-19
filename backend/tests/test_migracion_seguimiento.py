from sqlalchemy import inspect, text

from app.core import migraciones
from tests.apoyo_migraciones import conserva, volcado
from tests.test_migracion_pantallas import _base_en_0007
from tests.test_migracion_presencia import _bajar, _migrar

DATOS_0008 = """
INSERT INTO resultados
    (ronda_id, caso_id, usuario_email, estado, pasos_marcados, comentario, actualizado)
VALUES (1, 'A-GEN-02', 'ana@ejemplo.test', 'falla',
    '[{"paso": 0, "estado": "comentario", "comentario": "Lento"},
      {"paso": 1, "estado": "pasa", "comentario": "  "}, 2]',
    NULL, '2026-03-01 10:00:00');
INSERT INTO resultados
    (ronda_id, caso_id, usuario_email, estado, pasos_marcados, comentario, actualizado)
VALUES (2, 'A-GEN-03', 'beto@ejemplo.test', 'no_pude',
    '[{"paso": 0, "estado": "falla", "comentario": "Roto"}]',
    'Sin datos', '2026-03-02 10:00:00');
INSERT INTO resultados
    (ronda_id, caso_id, usuario_email, estado, pasos_marcados, comentario, actualizado)
VALUES (1, 'A-GEN-04', 'ana@ejemplo.test', 'pasa', '[]', 'Ya no cuenta', '2026-03-03 10:00:00')
"""
COLUMNAS_FALLA = {"plazo", "plazo_por", "resuelta_en", "resuelta_por"}


def _esquema_fallas(motor) -> str:
    with motor.connect() as conexion:
        consulta = text("SELECT sql FROM sqlite_master WHERE name = 'fallas'")
        return conexion.execute(consulta).scalar_one()


def _base_en_0008(tmp_path):
    motor = _base_en_0007(tmp_path)
    _migrar(motor, "0008", DATOS_0008)
    return motor


def test_0009_conserva_datos_y_siembra_los_comentarios(tmp_path) -> None:
    motor = _base_en_0008(tmp_path)
    antes = volcado(motor)
    _migrar(motor, "0009")
    despues = volcado(motor)
    assert set(despues) == set(antes) | {"comentarios_seguimiento", "seguimiento"}
    assert conserva(antes, despues)
    assert despues["seguimiento"] == []
    assert all(f[c] is None for f in despues["fallas"] for c in COLUMNAS_FALLA)
    sembrados = {
        (f["ronda_id"], f["caso_id"], f["usuario_email"], f["paso"], f["tipo"]): f
        for f in despues["comentarios_seguimiento"]
    }
    assert set(sembrados) == {
        (1, "A-GEN-02", "ana@ejemplo.test", 0, "paso"),
        (2, "A-GEN-03", "beto@ejemplo.test", 0, "paso"),
        (2, "A-GEN-03", "beto@ejemplo.test", -1, "no_pude"),
    }
    assert all(f["estado"] == "nuevo" and f["resuelto_en"] is None for f in sembrados.values())
    assert sembrados[(1, "A-GEN-02", "ana@ejemplo.test", 0, "paso")]["creado"].startswith(
        "2026-03-01 10:00:00"
    )
    with motor.connect() as conexion:
        inspector = inspect(conexion)
        columnas = {c["name"] for c in inspector.get_columns("fallas")}
        indices = {i["name"] for i in inspector.get_indexes("seguimiento")}
    assert COLUMNAS_FALLA <= columnas
    assert "ix_seguimiento_objeto" in indices
    motor.dispose()


def test_baja_a_0008_y_vuelve(tmp_path) -> None:
    motor = _base_en_0008(tmp_path)
    antes = volcado(motor)
    checks = _esquema_fallas(motor).count("CHECK")
    _migrar(motor, "0009")
    _bajar(motor, "0008")
    assert volcado(motor) == antes
    assert _esquema_fallas(motor).count("CHECK") == checks > 0
    _migrar(motor, "head")
    sin_pantallas = {k: v for k, v in antes.items() if k != "pantallas"}
    assert conserva(sin_pantallas, volcado(motor))
    assert len(volcado(motor)["comentarios_seguimiento"]) == 3
    assert migraciones.revision_actual(motor) == migraciones.revision_head() == "0010"
    motor.dispose()
