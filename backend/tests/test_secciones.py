from app.models.falla import SEVERIDADES
from app.services import contenido

SECCION = "primeros-pasos"
URL = f"/api/secciones/{SECCION}/resultado"


def _casos() -> list:
    return next(s for s in contenido.obtener().respuesta.secciones if s.id == SECCION).casos


def _estados(cliente, ronda_id) -> dict:
    mis = cliente.get(f"/api/mis-casos?ronda={ronda_id}").json()
    return {r["caso_id"]: r["estado"] for r in mis["resultados"]}


def test_pasa_solo_llena_pendientes(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    primero = _casos()[0].id
    validador.put(f"/api/resultados/{primero}", json={"ronda_id": ronda_id, "estado": "no_pude"})
    respuesta = validador.post(URL, data={"ronda_id": ronda_id, "estado": "pasa"})
    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "afectados": len(_casos()) - 1,
        "omitidos": 1,
        "falla_id": None,
    }
    estados = _estados(validador, ronda_id)
    assert estados[primero] == "no_pude"
    assert all(estados[c.id] == "pasa" for c in _casos()[1:])


def test_sobrescribir_reemplaza_los_marcados(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    primero = _casos()[0].id
    validador.put(f"/api/resultados/{primero}", json={"ronda_id": ronda_id, "estado": "no_pude"})
    datos = {"ronda_id": ronda_id, "estado": "pasa", "sobrescribir": "true"}
    assert validador.post(URL, data=datos).json()["omitidos"] == 0
    assert _estados(validador, ronda_id)[primero] == "pasa"


def test_falla_crea_una_sola_falla_con_la_maxima_severidad(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    sin_texto = validador.post(URL, data={"ronda_id": ronda_id, "estado": "falla"})
    assert sin_texto.status_code == 400
    respuesta = validador.post(
        URL, data={"ronda_id": ronda_id, "estado": "falla", "obtenido": "Nada carga"}
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["afectados"] == len(_casos())
    estados = _estados(validador, ronda_id)
    assert all(estados[c.id] == "falla" for c in _casos())
    fallas = cliente_de("coordinacion").get(f"/api/fallas?ronda={ronda_id}").json()
    assert len(fallas) == 1
    falla = fallas[0]
    esperada = min((c.severidad for c in _casos()), key=SEVERIDADES.index)
    assert falla["severidad"] == esperada
    assert falla["seccion_completa"] is True
    assert falla["seccion_id"] == SECCION
    assert falla["obtenido"].startswith("Toda la sección: ")
    assert falla["paso"] is None


def test_ronda_cerrada_da_409(cliente_de, ronda_id) -> None:
    cliente_de("coordinacion").patch(f"/api/rondas/{ronda_id}", json={"abierta": False})
    respuesta = cliente_de("validador").post(URL, data={"ronda_id": ronda_id, "estado": "pasa"})
    assert respuesta.status_code == 409


def test_acceso_de_solo_lectura_no_marca_secciones(cliente_de, ronda_id) -> None:
    cliente_de("coordinacion").put(
        "/api/accesos",
        json=[{"usuario_email": "sinrol@local.test", "paginas": ["tablero", "fallas"]}],
    )
    respuesta = cliente_de("sin-rol").post(URL, data={"ronda_id": ronda_id, "estado": "pasa"})
    assert respuesta.status_code == 403


def test_seccion_no_asignada_da_403(cliente_de, ronda_id) -> None:
    coordinacion = cliente_de("coordinacion")
    otra = next(s.id for s in contenido.obtener().respuesta.secciones if s.id != SECCION)
    coordinacion.put(
        f"/api/rondas/{ronda_id}/asignaciones",
        json=[{"usuario_email": "validador@local.test", "seccion_id": otra}],
    )
    respuesta = cliente_de("validador").post(URL, data={"ronda_id": ronda_id, "estado": "pasa"})
    assert respuesta.status_code == 403
