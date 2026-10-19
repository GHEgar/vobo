from datetime import date

from app.core.database import SessionLocal
from app.services import comentarios_seguimiento, fallas, seguimiento, vinculos
from tests.apoyo_proyectos import crear_proyecto, importar, paquete_movil, ronda
from tests.test_informe_fallas import _filas, _reportar
from tests.test_seguimiento import _comentar, _comentarios

COORDINACION = "coordinacion@local.test"
VALIDADOR = "validador@local.test"


def _avisos(cliente) -> list[dict]:
    return cliente.get("/api/avisos").json()


def _eventos(registro: dict) -> list[tuple]:
    return [(e["accion"], e["anterior"], e["nuevo"]) for e in registro["seguimiento"]]


def _comentario(cliente_de, ronda_id, caso_id="A-GEN-03") -> dict:
    _comentar(cliente_de("validador"), ronda_id, caso_id, "Lento")
    return next(
        c for c in _comentarios(cliente_de("coordinacion"), ronda_id) if c["caso_id"] == caso_id
    )


def test_esfuerzo_registra_evento_y_responsable(cliente_de, ronda_id) -> None:
    falla = _reportar(cliente_de("validador"), ronda_id, "C-CAT-01", "No filtra")
    assert falla["esfuerzo_horas"] is None and falla["principal"] is None
    coordinacion = cliente_de("coordinacion")
    url = f"/api/fallas/{falla['id']}"
    con = coordinacion.patch(url, json={"esfuerzo_horas": 6}).json()
    assert con["esfuerzo_horas"] == 6
    assert con["plazo_por"] == COORDINACION
    assert coordinacion.patch(url, json={"estado": "en_curso"}).json()["esfuerzo_horas"] == 6
    movido = coordinacion.patch(url, json={"esfuerzo_horas": 12.5}).json()
    sin = coordinacion.patch(url, json={"esfuerzo_horas": None}).json()
    assert sin["esfuerzo_horas"] is None and sin["plazo_por"] is None
    assert movido["esfuerzo_horas"] == 12.5
    assert [e for e in _eventos(sin) if e[0] == "esfuerzo"] == [
        ("esfuerzo", None, "6"),
        ("esfuerzo", "6", "12.5"),
        ("esfuerzo", "12.5", None),
    ]
    assert len(_avisos(cliente_de("validador"))) == 1
    assert coordinacion.patch(url, json={"esfuerzo_horas": 1001}).status_code == 422
    assert coordinacion.patch(url, json={"esfuerzo_horas": -1}).status_code == 422


def test_esfuerzo_en_comentario(cliente_de, ronda_id) -> None:
    comentario = _comentario(cliente_de, ronda_id)
    url = f"/api/comentarios/{comentario['id']}"
    hecho = cliente_de("coordinacion").patch(url, json={"esfuerzo_horas": 3}).json()
    assert hecho["esfuerzo_horas"] == 3 and hecho["plazo_por"] == COORDINACION
    assert _eventos(hecho) == [("esfuerzo", None, "3")]


def test_vincular_falla_con_falla_copia_plazo_y_propaga(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    principal = _reportar(cliente_de("coordinacion"), ronda_id, "C-CAT-01", "No filtra")
    seguidora = _reportar(validador, ronda_id, "C-CAT-02", "Tampoco ordena")
    coordinacion = cliente_de("coordinacion")
    url_p = f"/api/fallas/{principal['id']}"
    url_s = f"/api/fallas/{seguidora['id']}"
    coordinacion.patch(url_p, json={"plazo": "2026-11-05", "esfuerzo_horas": 4})
    ligada = coordinacion.patch(
        url_s, json={"principal": {"objeto": "falla", "id": principal["id"]}}
    ).json()
    etiqueta = f"#{principal['id']} · C-CAT-01"
    assert ligada["principal"] == {"objeto": "falla", "id": principal["id"], "etiqueta": etiqueta}
    assert ligada["plazo"] == "2026-11-05"
    assert _eventos(ligada) == [
        ("vinculo", None, f"falla:{principal['id']}"),
        ("plazo", None, "2026-11-05"),
    ]
    listado = {f["id"]: f for f in coordinacion.get(f"/api/fallas?ronda={ronda_id}").json()}
    assert listado[principal["id"]]["seguidores"] == 1
    coordinacion.patch(url_p, json={"estado": "lista_para_revalidar", "plazo": "2026-11-09"})
    actual = {f["id"]: f for f in coordinacion.get(f"/api/fallas?ronda={ronda_id}").json()}
    seguida = actual[seguidora["id"]]
    assert seguida["estado"] == "lista_para_revalidar" and seguida["plazo"] == "2026-11-09"
    propagados = [e for e in seguida["seguimiento"] if e["texto"] == etiqueta]
    assert [e["accion"] for e in propagados] == ["vinculo", "plazo", "plazo", "estado"]
    assert {e["autor_email"] for e in propagados} == {COORDINACION}
    [aviso] = _avisos(validador)
    assert aviso["falla_id"] == seguidora["id"]
    assert aviso["titulo"] == "Ya puedes volver a probar C-CAT-02"
    assert aviso["mensaje"].endswith("Plazo: 9 de noviembre de 2026")


def test_comentario_sigue_a_falla_con_mapeo(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    comentario = _comentario(cliente_de, ronda_id)
    falla = _reportar(cliente_de("coordinacion"), ronda_id, "C-CAT-01", "No filtra")
    coordinacion = cliente_de("coordinacion")
    url_c = f"/api/comentarios/{comentario['id']}"
    url_f = f"/api/fallas/{falla['id']}"
    ligado = coordinacion.patch(url_c, json={"principal": {"objeto": "falla", "id": falla["id"]}})
    assert ligado.json()["principal"]["etiqueta"] == f"#{falla['id']} · C-CAT-01"
    for estado_falla, esperado in (
        ("en_curso", "en_curso"),
        ("lista_para_revalidar", "en_curso"),
        ("cerrada", "resuelto"),
        ("nueva", "nuevo"),
    ):
        coordinacion.patch(url_f, json={"estado": estado_falla})
        [actual] = [c for c in _comentarios(coordinacion, ronda_id) if c["id"] == comentario["id"]]
        assert actual["estado"] == esperado
    assert actual["resuelto_en"] is None
    assert [a["titulo"] for a in _avisos(validador)] == [
        "Tu comentario en A-GEN-03 fue atendido",
        "Estamos trabajando en tu comentario en A-GEN-03",
    ]


def test_falla_sigue_a_comentario_con_mapeo(cliente_de, ronda_id) -> None:
    comentario = _comentario(cliente_de, ronda_id)
    falla = _reportar(cliente_de("validador"), ronda_id, "C-CAT-01", "No filtra")
    coordinacion = cliente_de("coordinacion")
    url_c = f"/api/comentarios/{comentario['id']}"
    ligada = coordinacion.patch(
        f"/api/fallas/{falla['id']}",
        json={"principal": {"objeto": "comentario", "id": comentario["id"]}},
    ).json()
    assert ligada["principal"]["etiqueta"] == "A-GEN-03 · paso 1"
    respuesta = coordinacion.patch(url_c, json={"estado": "resuelto"}).json()
    assert respuesta["seguidores"] == 1
    [actual] = coordinacion.get(f"/api/fallas?ronda={ronda_id}").json()
    assert actual["estado"] == "cerrada" and actual["resuelta_por"] == COORDINACION
    titulos = {a["falla_id"]: a["titulo"] for a in _avisos(cliente_de("validador"))}
    assert titulos == {
        falla["id"]: "Tu reporte de C-CAT-01 fue atendido",
        None: "Tu comentario en A-GEN-03 fue atendido",
    }


def test_desvincular_deja_el_estado(cliente_de, ronda_id) -> None:
    principal = _reportar(cliente_de("coordinacion"), ronda_id, "C-CAT-01", "No filtra")
    seguidora = _reportar(cliente_de("validador"), ronda_id, "C-CAT-02", "Tampoco")
    coordinacion = cliente_de("coordinacion")
    url_s = f"/api/fallas/{seguidora['id']}"
    coordinacion.patch(url_s, json={"principal": {"objeto": "falla", "id": principal["id"]}})
    coordinacion.patch(f"/api/fallas/{principal['id']}", json={"estado": "en_curso"})
    suelta = coordinacion.patch(url_s, json={"principal": None}).json()
    assert suelta["principal"] is None and suelta["estado"] == "en_curso"
    assert _eventos(suelta)[-1] == ("vinculo", f"falla:{principal['id']}", None)
    assert suelta["seguimiento"][-1]["texto"] == f"#{principal['id']} · C-CAT-01"
    coordinacion.patch(f"/api/fallas/{principal['id']}", json={"estado": "cerrada"})
    assert coordinacion.patch(url_s, json={"principal": None}).json()["estado"] == "en_curso"


def test_rechazos(cliente_de, ronda_id) -> None:
    coordinacion = cliente_de("coordinacion")
    a = _reportar(coordinacion, ronda_id, "C-CAT-01", "Uno")
    b = _reportar(coordinacion, ronda_id, "C-CAT-02", "Dos")
    c = _reportar(coordinacion, ronda_id, "A-GEN-01", "Tres")

    def ligar(origen: dict, destino_id: int, objeto: str = "falla"):
        cuerpo = {"principal": {"objeto": objeto, "id": destino_id}}
        return coordinacion.patch(f"/api/fallas/{origen['id']}", json=cuerpo)

    a_si_mismo = ligar(a, a["id"])
    assert a_si_mismo.status_code == 409 and "consigo mismo" in a_si_mismo.json()["detail"]
    assert ligar(a, 9999).status_code == 404
    assert ligar(a, 9999, "comentario").status_code == 404
    assert ligar(b, a["id"]).status_code == 200
    cadena = ligar(c, b["id"])
    assert cadena.status_code == 409 and "ya se resuelve con otro" in cadena.json()["detail"]
    con_seguidores = ligar(a, c["id"])
    assert con_seguidores.status_code == 409
    assert "principal de 1 reporte" in con_seguidores.json()["detail"]
    invalido = coordinacion.patch(
        f"/api/fallas/{a['id']}", json={"principal": {"objeto": "otro", "id": 1}}
    )
    assert invalido.status_code == 422


def test_rechaza_otro_proyecto(en_base, cliente_de, ronda_id) -> None:
    admin = cliente_de("administracion")
    crear_proyecto(admin)
    importar(admin, "movil", paquete_movil(admin))
    movil = ronda(admin, "Ronda móvil", "movil")
    ajena = _reportar(admin, movil, "M-APP-01", "No abre")
    propia = _reportar(admin, ronda_id, "C-CAT-01", "No filtra")
    respuesta = admin.patch(
        f"/api/fallas/{propia['id']}", json={"principal": {"objeto": "falla", "id": ajena["id"]}}
    )
    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "El reporte principal es de otro proyecto"


def test_permisos(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    a = _reportar(validador, ronda_id, "C-CAT-01", "Uno")
    b = _reportar(validador, ronda_id, "C-CAT-02", "Dos")
    url = f"/api/fallas/{a['id']}"
    assert validador.patch(url, json={"esfuerzo_horas": 2}).status_code == 403
    cuerpo = {"principal": {"objeto": "falla", "id": b["id"]}}
    assert validador.patch(url, json=cuerpo).status_code == 403
    comentario = _comentario(cliente_de, ronda_id)
    url_c = f"/api/comentarios/{comentario['id']}"
    assert validador.patch(url_c, json={"esfuerzo_horas": 2}).status_code == 403
    assert cliente_de(None).patch(url, json={"esfuerzo_horas": 2}).status_code == 401


def test_sumas_excluyen_seguidores(cliente_de, ronda_id) -> None:
    coordinacion = cliente_de("coordinacion")
    a = _reportar(coordinacion, ronda_id, "C-CAT-01", "Uno")
    b = _reportar(coordinacion, ronda_id, "C-CAT-02", "Dos")
    c = _reportar(coordinacion, ronda_id, "A-GEN-01", "Tres")
    comentario = _comentario(cliente_de, ronda_id)
    coordinacion.patch(f"/api/fallas/{a['id']}", json={"esfuerzo_horas": 6})
    coordinacion.patch(f"/api/fallas/{b['id']}", json={"esfuerzo_horas": 10, "estado": "cerrada"})
    coordinacion.patch(f"/api/fallas/{c['id']}", json={"esfuerzo_horas": 8})
    coordinacion.patch(
        f"/api/fallas/{c['id']}", json={"principal": {"objeto": "falla", "id": a["id"]}}
    )
    coordinacion.patch(f"/api/comentarios/{comentario['id']}", json={"esfuerzo_horas": 2})
    with SessionLocal() as db:
        registros = [fallas.obtener_o_404(db, f["id"]) for f in (a, b, c)]
        registros.append(comentarios_seguimiento.obtener_o_404(db, comentario["id"]))
        assert vinculos.sumar_esfuerzo(registros) == vinculos.Sumas(total=18, pendiente=8)
    filas = _filas(coordinacion.get(f"/api/fallas/informe.csv?ronda={ronda_id}"))
    por_id = {int(f["id"]): f for f in filas}
    assert list(filas[0])[-2:] == ["esfuerzo (h)", "se resuelve con"]
    assert por_id[c["id"]]["esfuerzo (h)"] == "8"
    assert por_id[c["id"]]["se resuelve con"] == f"#{a['id']} · C-CAT-01"
    assert por_id[a["id"]]["se resuelve con"] == ""


def test_funciones_publicas_fuera_de_la_api(cliente_de, ronda_id) -> None:
    a = _reportar(cliente_de("coordinacion"), ronda_id, "C-CAT-01", "Uno")
    b = _reportar(cliente_de("validador"), ronda_id, "C-CAT-02", "Dos")
    with SessionLocal() as db:
        principal = fallas.obtener_o_404(db, a["id"])
        principal.plazo = date(2026, 12, 1)
        fila = fallas.obtener_o_404(db, b["id"])
        assert seguimiento.cambiar_esfuerzo(db, "falla", fila, 5, COORDINACION)
        assert not seguimiento.cambiar_esfuerzo(db, "falla", fila, 5, COORDINACION)
        assert vinculos.vincular(db, "falla", fila, ("falla", a["id"]), COORDINACION)
        assert not vinculos.vincular(db, "falla", fila, ("falla", a["id"]), COORDINACION)
        db.commit()
    [guardada] = [
        f
        for f in cliente_de("coordinacion").get(f"/api/fallas?ronda={ronda_id}").json()
        if f["id"] == b["id"]
    ]
    assert guardada["esfuerzo_horas"] == 5 and guardada["plazo"] == "2026-12-01"
    assert [e[0] for e in _eventos(guardada)] == ["esfuerzo", "vinculo", "plazo"]
