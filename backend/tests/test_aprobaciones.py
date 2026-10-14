from app.services import contenido
from tests.conftest import TOKEN_LECTURA


def _herramienta_con_varias() -> tuple[str, list[str]]:
    actual = contenido.obtener()
    for herramienta_id in actual.herramientas:
        casos = [c for c, u in actual.casos.items() if u.caso.herramienta == herramienta_id]
        if len(casos) >= 2:
            return herramienta_id, casos
    raise AssertionError("El contenido no tiene una herramienta con dos casos")


def _aprobar(cliente, ronda_id, *items):
    cuerpo = [
        {"tipo": tipo, "objetivo_id": objetivo, "estado": estado, "comentario": ""}
        for tipo, objetivo, estado in items
    ]
    return cliente.post("/api/aprobaciones", json={"ronda_id": ronda_id, "items": cuerpo})


def _estado(respuesta, herramienta_id) -> dict:
    return next(
        h for h in respuesta.json()["herramientas"] if h["herramienta_id"] == herramienta_id
    )


def test_aprobar_herramienta_aprueba_sus_caracteristicas(cliente_de, ronda_id) -> None:
    herramienta, casos = _herramienta_con_varias()
    respuesta = _aprobar(
        cliente_de("aprobacion"), ronda_id, ("herramienta", herramienta, "aprobada")
    )
    assert respuesta.status_code == 201
    estado = _estado(respuesta, herramienta)
    assert estado["estado"] == "aprobada"
    assert {c["caso_id"]: c["estado"] for c in estado["caracteristicas"]} == dict.fromkeys(
        casos, "aprobada"
    )


def test_rechazo_explicito_sobrevive_a_aprobacion_posterior(cliente_de, ronda_id) -> None:
    herramienta, casos = _herramienta_con_varias()
    aprobador = cliente_de("aprobacion")
    _aprobar(aprobador, ronda_id, ("herramienta", herramienta, "aprobada"))
    _aprobar(aprobador, ronda_id, ("caracteristica", casos[0], "rechazada"))
    respuesta = _aprobar(aprobador, ronda_id, ("herramienta", herramienta, "aprobada"))
    estado = _estado(respuesta, herramienta)
    caracteristicas = {c["caso_id"]: c for c in estado["caracteristicas"]}
    assert caracteristicas[casos[0]]["estado"] == "rechazada"
    assert caracteristicas[casos[0]]["origen"] == "explicita"
    assert caracteristicas[casos[1]]["estado"] == "aprobada"
    assert estado["estado"] == "aprobada_parcial"
    assert len(estado["historial"]) == 2


def test_rechazar_herramienta_rechaza_todas(cliente_de, ronda_id) -> None:
    herramienta, casos = _herramienta_con_varias()
    aprobador = cliente_de("aprobacion")
    _aprobar(aprobador, ronda_id, ("caracteristica", casos[0], "aprobada"))
    respuesta = _aprobar(aprobador, ronda_id, ("herramienta", herramienta, "rechazada"))
    estado = _estado(respuesta, herramienta)
    assert estado["estado"] == "rechazada"
    assert all(c["estado"] == "rechazada" for c in estado["caracteristicas"])


def test_solo_aprobacion_puede_registrar(cliente_de, ronda_id) -> None:
    herramienta, _ = _herramienta_con_varias()
    for clave in ("validador", "coordinacion"):
        respuesta = _aprobar(cliente_de(clave), ronda_id, ("herramienta", herramienta, "aprobada"))
        assert respuesta.status_code == 403
    coordinacion = cliente_de("coordinacion")
    assert coordinacion.get(f"/api/aprobaciones?ronda={ronda_id}").status_code == 200
    cabecera = {"Authorization": f"Bearer {TOKEN_LECTURA}"}
    lectura = cliente_de(None).get(f"/api/aprobaciones?ronda={ronda_id}", headers=cabecera)
    assert lectura.status_code == 200
    assert cliente_de("validador").get(f"/api/aprobaciones?ronda={ronda_id}").status_code == 403


def test_aprobador_lee_tablero_pero_no_marca_casos(cliente_de, ronda_id) -> None:
    aprobador = cliente_de("aprobacion")
    paginas = aprobador.get("/api/auth/me").json()["usuario"]["paginas"]
    assert {"aprobaciones", "tablero", "fallas", "herramientas"} <= set(paginas)
    assert "rondas" not in paginas
    assert aprobador.get(f"/api/tablero?ronda={ronda_id}").status_code == 200
    respuesta = aprobador.put(
        "/api/resultados/A-GEN-01", json={"ronda_id": ronda_id, "estado": "pasa"}
    )
    assert respuesta.status_code == 403


def test_objetivo_inexistente_da_404(cliente_de, ronda_id) -> None:
    respuesta = _aprobar(
        cliente_de("aprobacion"), ronda_id, ("herramienta", "no-existe", "aprobada")
    )
    assert respuesta.status_code == 404
