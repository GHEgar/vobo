import io


def _reportar_falla(validador, ronda_id: int) -> dict:
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
    return respuesta.json()


def test_renombrar_ronda(cliente_de, ronda_id) -> None:
    coordinacion = cliente_de("coordinacion")
    respuesta = coordinacion.patch(f"/api/rondas/{ronda_id}", json={"nombre": "  Ronda piloto "})
    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "Ronda piloto"


def test_borrar_ronda_quita_todo_lo_suyo(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    marcado = validador.put(
        "/api/resultados/A-GEN-03", json={"ronda_id": ronda_id, "estado": "pasa"}
    )
    assert marcado.status_code == 200
    falla = _reportar_falla(validador, ronda_id)
    coordinacion = cliente_de("coordinacion")
    url_evidencia = falla["evidencias"][0]["url"]
    assert coordinacion.get(url_evidencia).status_code == 200
    assert coordinacion.delete(f"/api/rondas/{ronda_id}").status_code == 204
    assert all(r["id"] != ronda_id for r in coordinacion.get("/api/rondas").json())
    assert coordinacion.get(f"/api/fallas?ronda={ronda_id}").json() == []
    assert coordinacion.get(url_evidencia).status_code == 404
    assert coordinacion.delete(f"/api/rondas/{ronda_id}").status_code == 404


def test_validador_no_borra_rondas(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    assert validador.delete(f"/api/rondas/{ronda_id}").status_code == 403


def test_asignaciones_con_seccion_retirada_se_guardan_sin_ella(cliente_de, ronda_id) -> None:
    coordinacion = cliente_de("coordinacion")
    respuesta = coordinacion.put(
        f"/api/rondas/{ronda_id}/asignaciones",
        json=[
            {"usuario_email": "ana@ejemplo.test", "seccion_id": "primeros-pasos"},
            {"usuario_email": "ana@ejemplo.test", "seccion_id": "seccion-que-ya-no-existe"},
        ],
    )
    assert respuesta.status_code == 200
    assert [a["seccion_id"] for a in respuesta.json()] == ["primeros-pasos"]
