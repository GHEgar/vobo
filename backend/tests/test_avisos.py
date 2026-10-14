def _falla(cliente_de, ronda_id) -> dict:
    respuesta = cliente_de("validador").post(
        "/api/fallas",
        data={
            "ronda_id": ronda_id,
            "caso_id": "A-GEN-01",
            "obtenido": "No cargó",
            "reproducible": "siempre",
        },
    )
    assert respuesta.status_code == 201
    return respuesta.json()


def test_aviso_desde_falla_va_a_quien_reporto(cliente_de, ronda_id) -> None:
    falla = _falla(cliente_de, ronda_id)
    coordinacion = cliente_de("coordinacion")
    respuesta = coordinacion.post(
        "/api/avisos", json={"mensaje": "Ya quedó", "falla_id": falla["id"]}
    )
    assert respuesta.status_code == 201
    [aviso] = respuesta.json()
    assert aviso["usuario_email"] == "validador@local.test"
    assert aviso["caso_id"] == "A-GEN-01"
    assert aviso["titulo"] == "Tu reporte de A-GEN-01 fue atendido"
    assert aviso["autor_nombre"] == "Carlos Coordinación"
    assert aviso["leido"] is None


def test_aviso_libre_a_varias_personas(cliente_de) -> None:
    coordinacion = cliente_de("coordinacion")
    respuesta = coordinacion.post(
        "/api/avisos",
        json={
            "destinatarios": ["validador@local.test", "aprobacion@local.test"],
            "mensaje": "Mañana abre la ronda",
        },
    )
    assert respuesta.status_code == 201
    avisos = respuesta.json()
    assert {a["usuario_email"] for a in avisos} == {
        "validador@local.test",
        "aprobacion@local.test",
    }
    assert all(a["titulo"] == "Aviso de coordinación" and a["caso_id"] is None for a in avisos)


def test_aviso_invalido_se_rechaza(cliente_de) -> None:
    coordinacion = cliente_de("coordinacion")
    duplicados = {"destinatarios": ["a@b.c", "a@b.c"], "mensaje": "Hola"}
    assert coordinacion.post("/api/avisos", json=duplicados).status_code == 422
    assert coordinacion.post("/api/avisos", json={"mensaje": "Hola"}).status_code == 422
    vacio = {"destinatarios": ["a@b.c"], "mensaje": "  "}
    assert coordinacion.post("/api/avisos", json=vacio).status_code == 422
    inexistente = {"mensaje": "Hola", "falla_id": 999}
    assert coordinacion.post("/api/avisos", json=inexistente).status_code == 404


def test_solo_coordinacion_crea_y_ve_personas(cliente_de) -> None:
    validador = cliente_de("validador")
    aviso = {"destinatarios": ["aprobacion@local.test"], "mensaje": "Hola"}
    assert validador.post("/api/avisos", json=aviso).status_code == 403
    assert validador.get("/api/avisos/personas").status_code == 403
    personas = cliente_de("coordinacion").get("/api/avisos/personas")
    assert personas.status_code == 200
    emails = {p["email"] for p in personas.json()}
    assert {"validador@local.test", "coordinacion@local.test"} <= emails


def test_cada_quien_ve_los_suyos_y_marca(cliente_de) -> None:
    coordinacion = cliente_de("coordinacion")
    for mensaje in ("Uno", "Dos"):
        coordinacion.post(
            "/api/avisos", json={"destinatarios": ["validador@local.test"], "mensaje": mensaje}
        )
    coordinacion.post(
        "/api/avisos", json={"destinatarios": ["aprobacion@local.test"], "mensaje": "Otro"}
    )
    validador = cliente_de("validador")
    propios = validador.get("/api/avisos").json()
    assert [a["mensaje"] for a in propios] == ["Dos", "Uno"]
    assert validador.get("/api/avisos/no-leidos").json() == {"total": 2}
    marcado = validador.post(f"/api/avisos/{propios[0]['id']}/leido")
    assert marcado.status_code == 200
    assert marcado.json()["leido"] is not None
    assert validador.get("/api/avisos/no-leidos").json() == {"total": 1}
    assert validador.post("/api/avisos/leidos").status_code == 200
    assert validador.get("/api/avisos/no-leidos").json() == {"total": 0}
    aprobacion = cliente_de("aprobacion")
    ajeno = aprobacion.get("/api/avisos").json()
    assert [a["mensaje"] for a in ajeno] == ["Otro"]
    assert aprobacion.get("/api/avisos/no-leidos").json() == {"total": 1}
    assert validador.post(f"/api/avisos/{ajeno[0]['id']}/leido").status_code == 404
    assert aprobacion.get("/api/avisos/no-leidos").json() == {"total": 1}


def test_mutaciones_exigen_csrf(cliente_de) -> None:
    validador = cliente_de("validador")
    del validador.headers["X-CSRF-Token"]
    assert validador.post("/api/avisos/leidos").status_code == 403


def test_sin_sesion_da_401(cliente_de) -> None:
    assert cliente_de(None).get("/api/avisos").status_code == 401
