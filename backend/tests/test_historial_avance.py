from datetime import UTC, datetime

import pytest

from app.services import contenido, resultados

URL = "/api/historial/avance"


@pytest.fixture
def reloj(monkeypatch: pytest.MonkeyPatch):
    actual = {"momento": datetime(2026, 3, 1, 10, tzinfo=UTC)}
    monkeypatch.setattr(resultados, "utcnow", lambda: actual["momento"])

    def mover(dia: int, hora: int = 10) -> None:
        actual["momento"] = datetime(2026, 3, dia, hora, tzinfo=UTC)

    return mover


def _poner(cliente, ronda_id: int, caso: str, estado: str) -> None:
    cuerpo = {"ronda_id": ronda_id, "estado": estado}
    assert cliente.put(f"/api/resultados/{caso}", json=cuerpo).status_code == 200


def _historia(cliente_de, ronda_id: int, reloj) -> None:
    validador = cliente_de("validador")
    coordinacion = cliente_de("coordinacion")
    reloj(1)
    _poner(validador, ronda_id, "A-GEN-01", "pasa")
    _poner(validador, ronda_id, "A-GEN-03", "pasa")
    reloj(2, 9)
    _poner(coordinacion, ronda_id, "A-GEN-01", "falla")
    reloj(2, 23)
    _poner(validador, ronda_id, "A-GEN-03", "pendiente")
    _poner(validador, ronda_id, "A-GEN-01", "pendiente")
    reloj(4)
    _poner(validador, ronda_id, "E-GEN-01", "no_pude")


def test_avance_por_dia_desde_la_bitacora(cliente_de, ronda_id, reloj) -> None:
    _historia(cliente_de, ronda_id, reloj)
    total = len(contenido.obtener().casos)
    respuesta = cliente_de("coordinacion").get(f"{URL}?ronda={ronda_id}")
    assert respuesta.status_code == 200
    assert respuesta.json() == [
        {"fecha": "2026-03-01", "marcados_acumulados": 2, "total": total},
        {"fecha": "2026-03-02", "marcados_acumulados": 1, "total": total},
        {"fecha": "2026-03-03", "marcados_acumulados": 1, "total": total},
        {"fecha": "2026-03-04", "marcados_acumulados": 2, "total": total},
    ]


def test_avance_recorta_por_fechas_sin_perder_lo_previo(cliente_de, ronda_id, reloj) -> None:
    _historia(cliente_de, ronda_id, reloj)
    coordinacion = cliente_de("coordinacion")
    filtrado = coordinacion.get(f"{URL}?ronda={ronda_id}&desde=2026-03-02&hasta=2026-03-03")
    assert [p["marcados_acumulados"] for p in filtrado.json()] == [1, 1]
    assert [p["fecha"] for p in filtrado.json()] == ["2026-03-02", "2026-03-03"]
    hasta_el_uno = coordinacion.get(f"{URL}?ronda={ronda_id}&hasta=2026-03-01").json()
    assert [p["marcados_acumulados"] for p in hasta_el_uno] == [2]


def test_avance_del_proyecto_junta_sus_rondas(cliente_de, ronda_id, reloj) -> None:
    _historia(cliente_de, ronda_id, reloj)
    coordinacion = cliente_de("coordinacion")
    otra = coordinacion.post("/api/rondas", json={"nombre": "Ronda 2"}).json()["id"]
    reloj(3)
    _poner(cliente_de("validador"), otra, "C-CAT-01", "pasa")
    puntos = coordinacion.get(f"{URL}?proyecto=principal").json()
    assert [p["marcados_acumulados"] for p in puntos] == [2, 1, 2, 3]
    assert coordinacion.get(f"{URL}?ronda={otra}").json()[0]["fecha"] == "2026-03-03"


def test_sin_historial_da_lista_vacia(cliente_de, ronda_id) -> None:
    respuesta = cliente_de("coordinacion").get(f"{URL}?ronda={ronda_id}")
    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_avance_pide_permiso_de_seguimiento(cliente_de, ronda_id) -> None:
    assert cliente_de("validador").get(f"{URL}?ronda={ronda_id}").status_code == 403
    assert cliente_de("sin-rol").get(f"{URL}?ronda={ronda_id}").status_code == 403
    assert cliente_de(None).get(f"{URL}?ronda={ronda_id}").status_code == 401


def test_avance_valida_ronda_y_rango(cliente_de, ronda_id) -> None:
    coordinacion = cliente_de("coordinacion")
    assert coordinacion.get(f"{URL}?ronda=9999").status_code == 404
    invertido = coordinacion.get(f"{URL}?ronda={ronda_id}&desde=2026-03-05&hasta=2026-03-01")
    assert invertido.status_code == 422
    assert coordinacion.get(f"{URL}?desde=2020-01-01&hasta=2026-01-01").status_code == 422
