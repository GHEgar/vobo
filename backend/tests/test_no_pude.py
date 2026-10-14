import io

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 32


def _reportar(cliente, ronda_id, **extra):
    datos = {
        "ronda_id": ronda_id,
        "caso_id": "A-GEN-01",
        "obtenido": "Sin red en el edificio",
        "paso": 0,
    }
    datos.update(extra)
    return cliente.post(
        "/api/fallas",
        data=datos,
        files=[("imagenes", ("captura.png", io.BytesIO(PNG), "image/png"))],
    )


def test_no_pude_crea_registro_con_evidencia_y_marca_no_pude(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    respuesta = _reportar(validador, ronda_id, tipo="no_pude")
    assert respuesta.status_code == 201
    registro = respuesta.json()
    assert registro["tipo"] == "no_pude"
    assert len(registro["evidencias"]) == 1
    mis = validador.get(f"/api/mis-casos?ronda={ronda_id}").json()
    assert {r["caso_id"]: r["estado"] for r in mis["resultados"]}["A-GEN-01"] == "no_pude"
    coordinacion = cliente_de("coordinacion")
    tablero = coordinacion.get(f"/api/tablero?ronda={ronda_id}").json()
    criticas = next(c for c in tablero["criterios"] if c["clave"] == "criticas")
    assert criticas["cumple"] is True
    assert all(f["total"] == 0 for f in tablero["fallas"])
    solo_fallas = coordinacion.get(f"/api/fallas?ronda={ronda_id}&tipo=falla").json()
    solo_no_pude = coordinacion.get(f"/api/fallas?ronda={ronda_id}&tipo=no_pude").json()
    assert solo_fallas == []
    assert [f["id"] for f in solo_no_pude] == [registro["id"]]


def test_falla_por_omision_sigue_igual(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    assert _reportar(validador, ronda_id).status_code == 400
    respuesta = _reportar(validador, ronda_id, reproducible="siempre")
    assert respuesta.status_code == 201
    assert respuesta.json()["tipo"] == "falla"
    mis = validador.get(f"/api/mis-casos?ronda={ronda_id}").json()
    assert {r["caso_id"]: r["estado"] for r in mis["resultados"]}["A-GEN-01"] == "falla"
    tablero = cliente_de("coordinacion").get(f"/api/tablero?ronda={ronda_id}").json()
    assert next(c for c in tablero["criterios"] if c["clave"] == "criticas")["cumple"] is False


def test_paso_no_pude_se_acepta_en_resultados(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    respuesta = validador.put(
        "/api/resultados/A-GEN-03",
        json={
            "ronda_id": ronda_id,
            "estado": "no_pude",
            "pasos_marcados": [{"paso": 0, "estado": "no_pude"}],
        },
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["pasos_marcados"][0]["estado"] == "no_pude"
