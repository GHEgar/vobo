import json

import pytest

from tests.apoyo_proyectos import crear_proyecto, importar, marcar, paquete_movil, reportar, ronda

CORREOS = ("validador@local.test", "coordinacion@local.test", "local.test")


@pytest.fixture(autouse=True)
def sin_cache():
    from app.services import pantalla_datos

    pantalla_datos.olvidar()
    yield
    pantalla_datos.olvidar()


@pytest.fixture
def admin(en_base, cliente_de):
    return cliente_de("administracion")


def _token(admin, **extra) -> str:
    respuesta = admin.post("/api/admin/pantallas", json={"nombre": "Sala", **extra})
    return respuesta.json()["enlace"].rsplit("/", 1)[1]


def _datos(cliente_de, token: str) -> dict:
    respuesta = cliente_de(None).get(f"/api/pantalla/{token}/datos")
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()


def _escenario(admin, cliente_de) -> tuple[int, int]:
    crear_proyecto(admin)
    importar(admin, "movil", paquete_movil(admin))
    principal = ronda(admin, "Ronda 3")
    movil = ronda(admin, "Ronda móvil", "movil")
    validador = cliente_de("validador")
    coordinacion = cliente_de("coordinacion")
    comentario = {"ronda_id": principal, "estado": "pasa", "comentario": "secreto-del-comentario"}
    assert validador.put("/api/resultados/A-GEN-01", json=comentario).status_code == 200
    assert marcar(validador, principal, "C-PED-01", "falla").status_code == 200
    assert marcar(validador, movil, "M-APP-01").status_code == 200
    assert marcar(coordinacion, principal, "A-GEN-01", "no_pude").status_code == 200
    assert reportar(validador, principal, "C-PED-01", "obtenido-privado").status_code == 201
    presencia = {"ruta": "/caso/A-GEN-03", "caso_id": "A-GEN-03", "ronda_id": principal}
    assert validador.post("/api/presencia", json=presencia).status_code == 204
    return principal, movil


def test_resumen_por_proyecto(admin, cliente_de) -> None:
    _escenario(admin, cliente_de)
    datos = _datos(cliente_de, _token(admin))
    principal, movil = datos["proyectos"]
    assert principal["clave"] == "principal" and movil["clave"] == "movil"
    assert principal["color"] == "#3987E5" and movil["color"] == "#D95926"
    assert principal["ronda"] == {"nombre": "Ronda 3", "dia": 1}
    assert principal["conteos"]["pasa"] == 1 and principal["conteos"]["falla"] == 1
    assert principal["total"] == sum(principal["conteos"].values())
    assert principal["fallas_abiertas"] == 1
    assert principal["en_linea"] == 1 and movil["en_linea"] == 0
    assert movil["conteos"]["pasa"] == 1 and movil["avance"] > 0
    assert principal["agrupado"] is False
    assert "Catálogo" in {s["nombre"] for s in principal["sistemas"]}
    casos = [c for s in principal["sistemas"] for sec in s["secciones"] for c in sec["casos"]]
    assert {"id": "C-PED-01", "estado": "falla"} in casos


def test_participacion_y_avance_individual(admin, cliente_de) -> None:
    principal, _ = _escenario(admin, cliente_de)
    asignar = [{"usuario_email": "coordinacion@local.test", "seccion_id": "primeros-pasos"}]
    respuesta = admin.put(f"/api/rondas/{principal}/asignaciones", json=asignar)
    assert respuesta.status_code in (200, 204), respuesta.text
    personas = {p["nombre"]: p for p in _datos(cliente_de, _token(admin))["personas"]}
    valeria, carlos = personas["Valeria"], personas["Carlos"]
    assert valeria["iniciales"] == "VV" and carlos["iniciales"] == "CC"
    assert valeria["participa"] == {"principal": 2, "movil": 1}
    assert carlos["participa"] == {"principal": 1}
    assert valeria["activa"] is True and carlos["activa"] is False
    assert valeria["actual"] == {
        "proyecto": "principal",
        "caso_id": "A-GEN-03",
        "seccion_id": "primeros-pasos",
    }
    assert carlos["asignados"] == 4 and carlos["marcados"] == 1
    assert carlos["avance"] == 0.25
    assert valeria["asignados"] == 13 and valeria["marcados"] == 3
    assert valeria["color"].startswith("#") and len(valeria["id"]) == 16


def test_sin_correos_tokens_comentarios_ni_evidencias(admin, cliente_de) -> None:
    _escenario(admin, cliente_de)
    token = _token(admin)
    texto = json.dumps(_datos(cliente_de, token))
    for prohibido in (*CORREOS, token, "secreto-del-comentario", "obtenido-privado", "@"):
        assert prohibido not in texto
    assert "evidencias" not in texto and "ruta" not in texto
    publica = cliente_de(None).get(f"/api/pantalla/{token}").text
    assert "@" not in publica and token not in publica


def test_cinta_de_eventos(admin, cliente_de) -> None:
    _escenario(admin, cliente_de)
    eventos = _datos(cliente_de, _token(admin))["eventos"]
    textos = {(e["quien"], e["texto"]) for e in eventos}
    assert ("Valeria", "marcó C-PED-01 · Falla") in textos
    assert ("Valeria", "reportó una falla en C-PED-01") in textos
    assert ("Valeria", "marcó M-APP-01 · Pasa") in textos
    assert ("Carlos", "marcó A-GEN-01 · No pude") in textos
    assert len(eventos) <= 20
    assert [e["cuando"] for e in eventos] == sorted((e["cuando"] for e in eventos), reverse=True)


def test_agrupa_por_seccion_sobre_el_umbral(admin, cliente_de, monkeypatch) -> None:
    from app.services import pantalla_proyectos

    _escenario(admin, cliente_de)
    monkeypatch.setattr(pantalla_proyectos, "UMBRAL_CASOS", 5)
    principal, movil = _datos(cliente_de, _token(admin))["proyectos"]
    assert principal["agrupado"] is True and movil["agrupado"] is False
    secciones = [sec for s in principal["sistemas"] for sec in s["secciones"]]
    assert all(sec["casos"] is None for sec in secciones)
    primeros = next(sec for sec in secciones if sec["id"] == "primeros-pasos")
    assert primeros["conteos"] == {"pasa": 1, "falla": 0, "no_pude": 0, "pendiente": 2}
    assert primeros["avance"] == 0.3333
    assert movil["sistemas"][0]["secciones"][0]["casos"] is not None


def test_cache_de_quince_segundos(admin, cliente_de, monkeypatch) -> None:
    from app.services import pantalla_datos

    principal, _ = _escenario(admin, cliente_de)
    token = _token(admin)
    llamadas = []
    original = pantalla_datos.calcular
    monkeypatch.setattr(
        pantalla_datos, "calcular", lambda db, p: llamadas.append(1) or original(db, p)
    )
    primero = _datos(cliente_de, token)
    marcar(cliente_de("validador"), principal, "C-PED-02")
    assert _datos(cliente_de, token) == primero
    assert len(llamadas) == 1
    reloj = pantalla_datos.time.monotonic() + pantalla_datos.VIGENCIA + 1
    monkeypatch.setattr(pantalla_datos.time, "monotonic", lambda: reloj)
    tercero = _datos(cliente_de, token)
    assert len(llamadas) == 2
    antes = primero["proyectos"][0]["conteos"]["pasa"]
    assert tercero["proyectos"][0]["conteos"]["pasa"] == antes + 1


def test_sin_ronda_abierta(admin, cliente_de) -> None:
    [proyecto] = _datos(cliente_de, _token(admin))["proyectos"]
    assert proyecto["ronda"] is None
    assert proyecto["conteos"]["pendiente"] == proyecto["total"] > 0
    assert proyecto["fallas_abiertas"] == 0
