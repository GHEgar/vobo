import io


def _marcar_todo(cliente, ronda_id, casos, estado="pasa") -> None:
    for caso_id in casos:
        respuesta = cliente.put(
            f"/api/resultados/{caso_id}", json={"ronda_id": ronda_id, "estado": estado}
        )
        assert respuesta.status_code == 200


def _casos(cliente) -> list[str]:
    contenido = cliente.get("/api/contenido").json()
    return [c["id"] for s in contenido["secciones"] for c in s["casos"]]


def test_sin_ejecutar_no_sale(cliente_de, ronda_id) -> None:
    coordinacion = cliente_de("coordinacion")
    tablero = coordinacion.get(f"/api/tablero?ronda={ronda_id}").json()
    assert tablero["veredicto"] == "No sale"
    ejecucion = next(c for c in tablero["criterios"] if c["clave"] == "ejecucion")
    assert not ejecucion["cumple"]


def test_no_pude_cuenta_como_no_pasado(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    casos = _casos(validador)
    _marcar_todo(validador, ronda_id, casos[1:])
    _marcar_todo(validador, ronda_id, casos[:1], "no_pude")
    tablero = cliente_de("coordinacion").get(f"/api/tablero?ronda={ronda_id}").json()
    assert tablero["veredicto"] == "No sale"
    assert tablero["casos_ejecutados"] == len(casos) - 1
    fila = next(p for p in tablero["personas"] if p["email"] == "validador@local.test")
    assert sum(c["no_pude"] for c in fila["celdas"]) == 1


def test_critica_abierta_bloquea_y_al_cerrarla_sale(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    casos = _casos(validador)
    _marcar_todo(validador, ronda_id, casos)
    imagen = io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"0" * 32)
    respuesta = validador.post(
        "/api/fallas",
        data={
            "ronda_id": ronda_id,
            "caso_id": "A-GEN-01",
            "obtenido": "No cargó",
            "reproducible": "siempre",
            "paso": 0,
        },
        files=[("imagenes", ("captura.png", imagen, "image/png"))],
    )
    assert respuesta.status_code == 201
    falla = respuesta.json()
    assert falla["severidad"] == "critica"
    assert len(falla["evidencias"]) == 1
    coordinacion = cliente_de("coordinacion")
    tablero = coordinacion.get(f"/api/tablero?ronda={ronda_id}").json()
    assert tablero["veredicto"] == "No sale"
    assert not next(c for c in tablero["criterios"] if c["clave"] == "criticas")["cumple"]
    assert coordinacion.get(falla["evidencias"][0]["url"]).status_code == 200
    cerrada = coordinacion.patch(
        f"/api/fallas/{falla['id']}", json={"estado": "cerrada", "nota_resolucion": "Corregido"}
    )
    assert cerrada.status_code == 200
    tablero = coordinacion.get(f"/api/tablero?ronda={ronda_id}").json()
    assert tablero["veredicto"] == "Sale"
    assert tablero["razones"] == []


def test_evidencia_que_no_es_imagen_se_rechaza(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    respuesta = validador.post(
        "/api/fallas",
        data={
            "ronda_id": ronda_id,
            "caso_id": "A-GEN-01",
            "obtenido": "No cargó",
            "reproducible": "una_vez",
        },
        files=[("imagenes", ("nota.png", io.BytesIO(b"no soy imagen"), "image/png"))],
    )
    assert respuesta.status_code == 400
