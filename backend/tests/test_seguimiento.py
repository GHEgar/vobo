from tests.test_informe_fallas import _filas, _reportar

COORDINACION = "coordinacion@local.test"
VALIDADOR = "validador@local.test"


def _fallas(cliente, ronda_id) -> dict[int, dict]:
    return {f["id"]: f for f in cliente.get(f"/api/fallas?ronda={ronda_id}").json()}


def _comentar(cliente, ronda_id, caso_id, texto, paso=0) -> None:
    marcados = [{"paso": paso, "estado": "comentario", "comentario": texto}] if texto else []
    respuesta = cliente.put(
        f"/api/resultados/{caso_id}",
        json={"ronda_id": ronda_id, "estado": "pendiente", "pasos_marcados": marcados},
    )
    assert respuesta.status_code == 200


def _comentarios(cliente, ronda_id) -> list[dict]:
    return cliente.get(f"/api/comentarios?ronda={ronda_id}").json()


def test_estado_cierre_y_reapertura(cliente_de, ronda_id) -> None:
    falla = _reportar(cliente_de("validador"), ronda_id, "C-CAT-01", "No filtra")
    assert falla["seguimiento"] == [] and falla["resuelta_en"] is None
    coordinacion = cliente_de("coordinacion")
    url = f"/api/fallas/{falla['id']}"
    en_curso = coordinacion.patch(url, json={"estado": "en_curso"}).json()
    assert en_curso["resuelta_en"] is None
    cerrada = coordinacion.patch(url, json={"estado": "cerrada"}).json()
    assert cerrada["resuelta_en"] is not None
    assert cerrada["resuelta_por"] == COORDINACION
    assert cerrada["resuelta_por_nombre"] == "Carlos Coordinación"
    assert (
        coordinacion.patch(url, json={"estado": "cerrada"}).json()["seguimiento"]
        == (cerrada["seguimiento"])
    )
    reabierta = coordinacion.patch(url, json={"estado": "nueva"}).json()
    assert reabierta["resuelta_en"] is None and reabierta["resuelta_por"] is None
    eventos = [(e["accion"], e["anterior"], e["nuevo"]) for e in reabierta["seguimiento"]]
    assert eventos == [
        ("estado", "nueva", "en_curso"),
        ("estado", "en_curso", "cerrada"),
        ("estado", "cerrada", "nueva"),
    ]
    assert {e["autor"] for e in reabierta["seguimiento"]} == {"Carlos Coordinación"}


def test_nota_y_plazo(cliente_de, ronda_id) -> None:
    falla = _reportar(cliente_de("validador"), ronda_id, "C-CAT-01", "No filtra")
    coordinacion = cliente_de("coordinacion")
    url = f"/api/fallas/{falla['id']}"
    con_nota = coordinacion.patch(url, json={"nota_resolucion": " Corregido en 2.1 "}).json()
    assert con_nota["nota_resolucion"] == "Corregido en 2.1"
    coordinacion.patch(url, json={"nota_resolucion": "Corregido en 2.1"})
    con_plazo = coordinacion.patch(url, json={"plazo": "2026-11-05"}).json()
    assert con_plazo["plazo"] == "2026-11-05"
    assert con_plazo["plazo_por"] == COORDINACION
    assert con_plazo["plazo_por_nombre"] == "Carlos Coordinación"
    sin_tocar = coordinacion.patch(url, json={"estado": "en_curso"}).json()
    assert sin_tocar["plazo"] == "2026-11-05"
    sin_plazo = coordinacion.patch(url, json={"plazo": None}).json()
    assert sin_plazo["plazo"] is None and sin_plazo["plazo_por"] is None
    eventos = [
        (e["accion"], e["texto"], e["anterior"], e["nuevo"]) for e in sin_plazo["seguimiento"]
    ]
    assert eventos == [
        ("nota", "Corregido en 2.1", None, None),
        ("plazo", "", None, "2026-11-05"),
        ("estado", "", "nueva", "en_curso"),
        ("plazo", "", "2026-11-05", None),
    ]


def test_respuestas_de_falla(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    falla = _reportar(validador, ronda_id, "C-CAT-01", "No filtra")
    coordinacion = cliente_de("coordinacion")
    url = f"/api/fallas/{falla['id']}/respuestas"
    respuesta = coordinacion.post(url, json={"texto": "  Lo reviso hoy  "})
    assert respuesta.status_code == 201
    evento = respuesta.json()
    assert evento["accion"] == "respuesta" and evento["texto"] == "Lo reviso hoy"
    assert evento["autor"] == "Carlos Coordinación"
    assert coordinacion.post(url, json={"texto": "   "}).status_code == 422
    assert coordinacion.post(url, json={"texto": "x" * 4001}).status_code == 422
    assert validador.post(url, json={"texto": "Hola"}).status_code == 403
    assert coordinacion.post("/api/fallas/999/respuestas", json={"texto": "a"}).status_code == 404
    [listada] = _fallas(coordinacion, ronda_id).values()
    assert [e["texto"] for e in listada["seguimiento"]] == ["Lo reviso hoy"]


def test_validador_no_cambia_plazo(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    falla = _reportar(validador, ronda_id, "C-CAT-01", "No filtra")
    respuesta = validador.patch(f"/api/fallas/{falla['id']}", json={"plazo": "2026-11-05"})
    assert respuesta.status_code == 403


def test_comentario_nace_con_seguimiento(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    _comentar(validador, ronda_id, "A-GEN-03", "Lento")
    [comentario] = _comentarios(cliente_de("coordinacion"), ronda_id)
    assert comentario["id"] is not None
    assert comentario["estado"] == "nuevo"
    assert comentario["creado"] is not None
    assert comentario["seguimiento"] == []
    _comentar(validador, ronda_id, "A-GEN-03", "Lento")
    [igual] = _comentarios(cliente_de("coordinacion"), ronda_id)
    assert igual["id"] == comentario["id"]


def test_resolver_y_reabrir_comentario(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    _comentar(validador, ronda_id, "A-GEN-03", "Lento")
    coordinacion = cliente_de("coordinacion")
    [comentario] = _comentarios(coordinacion, ronda_id)
    url = f"/api/comentarios/{comentario['id']}"
    resuelto = coordinacion.patch(url, json={"estado": "resuelto", "plazo": "2026-11-01"}).json()
    assert resuelto["estado"] == "resuelto"
    assert resuelto["resuelto_por"] == COORDINACION
    assert resuelto["resuelto_por_nombre"] == "Carlos Coordinación"
    assert resuelto["resuelto_en"] is not None
    assert resuelto["plazo"] == "2026-11-01" and resuelto["plazo_por"] == COORDINACION
    _comentar(validador, ronda_id, "A-GEN-03", "Lento")
    assert _comentarios(coordinacion, ronda_id)[0]["estado"] == "resuelto"
    _comentar(validador, ronda_id, "A-GEN-03", "Sigue lento")
    [reabierto] = _comentarios(coordinacion, ronda_id)
    assert reabierto["id"] == comentario["id"]
    assert reabierto["estado"] == "nuevo" and reabierto["resuelto_en"] is None
    ultimo = reabierto["seguimiento"][-1]
    assert (ultimo["accion"], ultimo["anterior"], ultimo["nuevo"]) == (
        "estado",
        "resuelto",
        "nuevo",
    )
    assert ultimo["autor_email"] == VALIDADOR


def test_respuestas_y_permisos_de_comentario(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    _comentar(validador, ronda_id, "A-GEN-03", "Lento")
    coordinacion = cliente_de("coordinacion")
    [comentario] = _comentarios(coordinacion, ronda_id)
    url = f"/api/comentarios/{comentario['id']}"
    assert validador.patch(url, json={"estado": "en_curso"}).status_code == 403
    assert validador.post(f"{url}/respuestas", json={"texto": "Hola"}).status_code == 403
    respuesta = coordinacion.post(f"{url}/respuestas", json={"texto": "Ya se optimizó"})
    assert respuesta.status_code == 201
    propios = validador.get(f"/api/comentarios/caso/A-GEN-03?ronda={ronda_id}").json()
    assert [e["texto"] for e in propios[0]["seguimiento"]] == ["Ya se optimizó"]
    assert coordinacion.patch("/api/comentarios/999", json={"estado": "nuevo"}).status_code == 404


def test_comentario_borrado_no_se_lista(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    _comentar(validador, ronda_id, "A-GEN-03", "Lento")
    coordinacion = cliente_de("coordinacion")
    [comentario] = _comentarios(coordinacion, ronda_id)
    _comentar(validador, ronda_id, "A-GEN-03", "")
    assert _comentarios(coordinacion, ronda_id) == []
    url = f"/api/comentarios/{comentario['id']}"
    assert coordinacion.patch(url, json={"estado": "resuelto"}).status_code == 404
    _comentar(validador, ronda_id, "A-GEN-03", "Volvió")
    [devuelto] = _comentarios(coordinacion, ronda_id)
    assert devuelto["id"] == comentario["id"]


def test_no_pude_tiene_seguimiento(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    validador.put(
        "/api/resultados/A-GEN-01",
        json={"ronda_id": ronda_id, "estado": "no_pude", "comentario": "Sin red"},
    )
    [comentario] = _comentarios(cliente_de("coordinacion"), ronda_id)
    assert comentario["tipo"] == "no_pude" and comentario["id"] is not None


def test_csv_con_plazo_resolucion_y_respuestas(cliente_de, ronda_id) -> None:
    falla = _reportar(cliente_de("validador"), ronda_id, "C-CAT-01", "No filtra")
    coordinacion = cliente_de("coordinacion")
    url = f"/api/fallas/{falla['id']}"
    coordinacion.patch(url, json={"plazo": "2026-11-05"})
    coordinacion.post(f"{url}/respuestas", json={"texto": "En eso"})
    coordinacion.patch(url, json={"estado": "cerrada"})
    [fila] = _filas(coordinacion.get("/api/fallas/informe.csv"))
    assert list(fila)[20:] == [
        "plazo",
        "responsable",
        "resuelta",
        "resolvió",
        "tiempo de solución (horas)",
        "respuestas",
        "esfuerzo (h)",
        "se resuelve con",
    ]
    assert fila["plazo"] == "2026-11-05"
    assert fila["responsable"] == "Carlos Coordinación"
    assert fila["resolvió"] == "Carlos Coordinación"
    assert len(fila["resuelta"]) == 16
    assert fila["tiempo de solución (horas)"] == "0.0"
    assert fila["respuestas"].endswith(" · Carlos Coordinación: En eso")
