def _otorgar(cliente_de, paginas) -> None:
    coordinacion = cliente_de("coordinacion")
    respuesta = coordinacion.put(
        "/api/accesos", json=[{"usuario_email": "validador@local.test", "paginas": paginas}]
    )
    assert respuesta.status_code == 200


def test_sin_acceso_otorgado_recibe_403(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    assert validador.get(f"/api/tablero?ronda={ronda_id}").status_code == 403
    assert validador.get("/api/fallas").status_code == 403
    assert validador.get("/api/comentarios").status_code == 403
    assert validador.get("/api/auth/me").json()["usuario"]["paginas"] == []


def test_acceso_otorgado_lee_pero_no_gestiona(cliente_de, ronda_id) -> None:
    _otorgar(cliente_de, ["tablero", "fallas", "herramientas"])
    validador = cliente_de("validador")
    sesion = validador.get("/api/auth/me").json()["usuario"]
    assert sesion["paginas"] == ["fallas", "herramientas", "tablero"]
    assert validador.get(f"/api/tablero?ronda={ronda_id}").status_code == 200
    assert validador.get("/api/fallas").status_code == 200
    assert validador.get("/api/comentarios").status_code == 200
    validador.post(
        "/api/fallas",
        data={
            "ronda_id": ronda_id,
            "caso_id": "A-GEN-01",
            "obtenido": "No cargó",
            "reproducible": "siempre",
        },
    )
    falla = validador.get("/api/fallas").json()[0]
    assert (
        validador.patch(f"/api/fallas/{falla['id']}", json={"estado": "cerrada"}).status_code == 403
    )
    assert (
        validador.put(
            "/api/decisiones/cualquiera", json={"ronda_id": ronda_id, "decision": "aplazar"}
        ).status_code
        == 403
    )
    assert validador.put("/api/accesos", json=[]).status_code == 403
    assert validador.post("/api/rondas", json={"nombre": "R2"}).status_code == 403


def test_solo_tablero_no_abre_fallas(cliente_de, ronda_id) -> None:
    _otorgar(cliente_de, ["tablero"])
    validador = cliente_de("validador")
    assert validador.get(f"/api/tablero?ronda={ronda_id}").status_code == 200
    assert validador.get("/api/fallas").status_code == 403


def test_coordinacion_ve_permisos_de_los_usuarios(cliente_de, ronda_id) -> None:
    cliente_de("validador")
    usuarios = cliente_de("coordinacion").get("/api/rondas/usuarios").json()
    validador = next(u for u in usuarios if u["email"] == "validador@local.test")
    assert validador["permisos"] == ["validacion.casos.ejecutar"]
    assert "rondas" in cliente_de("coordinacion").get("/api/auth/me").json()["usuario"]["paginas"]
