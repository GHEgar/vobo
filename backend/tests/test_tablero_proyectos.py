from app.services import contenido
from tests.conftest import TOKEN_LECTURA


def _seccion_de(sistema: str) -> str:
    return next(
        s.id for s in contenido.obtener().respuesta.secciones if s.sistema == sistema and s.casos
    )


def test_por_proyecto_respeta_asignaciones_y_cobertura(cliente_de, ronda_id) -> None:
    proyectos = sorted({s.sistema for s in contenido.obtener().respuesta.secciones if s.casos})
    elegido, otro = proyectos[0], proyectos[1]
    seccion = _seccion_de(elegido)
    coordinacion = cliente_de("coordinacion")
    coordinacion.put(
        f"/api/rondas/{ronda_id}/asignaciones",
        json=[{"usuario_email": "validador@local.test", "seccion_id": seccion}],
    )
    validador = cliente_de("validador")
    caso = next(s for s in contenido.obtener().respuesta.secciones if s.id == seccion).casos[0]
    validador.put(f"/api/resultados/{caso.id}", json={"ronda_id": ronda_id, "estado": "falla"})
    coordinacion.put("/api/resultados/A-GEN-01", json={"ronda_id": ronda_id, "estado": "pasa"})
    cabecera = {"Authorization": f"Bearer {TOKEN_LECTURA}"}
    tablero = cliente_de(None).get(f"/api/tablero?ronda={ronda_id}", headers=cabecera).json()
    assert tablero["proyectos"] == proyectos
    fila = tablero["por_proyecto"]["validador@local.test"]
    assert fila[elegido]["asignado"] is True
    assert fila[elegido]["hechos"] == 1
    assert fila[elegido]["falla"] == 1
    assert fila[otro]["asignado"] is False
    assert fila[otro]["total"] == 0
    todo = tablero["por_proyecto"]["coordinacion@local.test"]
    assert all(c["asignado"] for c in todo.values())
    assert tablero["cobertura"][elegido] == 2
    assert tablero["cobertura"][otro] == 1


def test_proyecto_sin_nadie_queda_en_cero(cliente_de, ronda_id) -> None:
    proyectos = sorted({s.sistema for s in contenido.obtener().respuesta.secciones if s.casos})
    coordinacion = cliente_de("coordinacion")
    coordinacion.put(
        f"/api/rondas/{ronda_id}/asignaciones",
        json=[{"usuario_email": "validador@local.test", "seccion_id": _seccion_de(proyectos[0])}],
    )
    tablero = coordinacion.get(f"/api/tablero?ronda={ronda_id}").json()
    assert tablero["cobertura"][proyectos[0]] == 1
    assert all(tablero["cobertura"][p] == 0 for p in proyectos[1:])
