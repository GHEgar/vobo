from tests.conftest import TOKEN_LECTURA


def _marcar(cliente, ronda_id: int, caso_id: str, estado: str) -> None:
    respuesta = cliente.put(
        f"/api/resultados/{caso_id}", json={"ronda_id": ronda_id, "estado": estado}
    )
    assert respuesta.status_code == 200


def test_grafo_con_el_contrato_de_tequio(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    _marcar(validador, ronda_id, "A-GEN-01", "pasa")
    _marcar(validador, ronda_id, "C-CAT-01", "falla")
    coordinacion = cliente_de("coordinacion")
    _marcar(coordinacion, ronda_id, "C-CAT-02", "no_pude")
    datos = coordinacion.get("/api/participacion").json()
    assert [s["key"] for s in datos["statuses"]] == ["pasa", "falla", "no_pude", "pendiente"]
    assert [s["tone"] for s in datos["statuses"]] == ["good", "critical", "warning", "neutral"]
    [proyecto] = datos["projects"]
    assert proyecto["id"] == "principal"
    assert proyecto["counts"]["pasa"] == 1
    assert proyecto["counts"]["falla"] == 1
    assert proyecto["counts"]["no_pude"] == 1
    total = sum(proyecto["counts"].values())
    assert proyecto["progress"] == round(3 / total, 4)
    assert {"label": "Ronda", "value": "Ronda 1"} in proyecto["details"]
    personas = {p["name"]: p for p in datos["people"]}
    assert personas["Valeria Validadora"]["metric"] == 2
    assert personas["Valeria Validadora"]["active"] is False
    enlaces = {(e["person"], e["project"]): e["weight"] for e in datos["links"]}
    assert enlaces[(personas["Valeria Validadora"]["id"], "principal")] == 2
    assert len(enlaces) == 2


def test_sin_correos_ni_nulos(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    _marcar(validador, ronda_id, "A-GEN-01", "pasa")
    respuesta = cliente_de("coordinacion").get("/api/participacion")
    assert "@" not in respuesta.text
    assert "null" not in respuesta.text
    [persona] = respuesta.json()["people"]
    assert len(persona["id"]) == 16


def test_pendientes_no_cuentan_como_trabajo(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    _marcar(validador, ronda_id, "A-GEN-01", "pendiente")
    datos = cliente_de("coordinacion").get("/api/participacion").json()
    assert datos["people"] == []
    assert datos["links"] == []
    assert datos["projects"][0]["progress"] == 0.0


def test_filtros_y_permisos(cliente_de, ronda_id) -> None:
    _marcar(cliente_de("validador"), ronda_id, "A-GEN-01", "pasa")
    coordinacion = cliente_de("coordinacion")
    assert coordinacion.get("/api/participacion?proyectos=no-existe").json()["projects"] == []
    con_ronda = coordinacion.get(f"/api/participacion?proyectos=principal&ronda={ronda_id}").json()
    assert con_ronda["projects"][0]["counts"]["pasa"] == 1
    otra = coordinacion.get(f"/api/participacion?proyectos=principal&ronda={ronda_id + 99}").json()
    assert otra["projects"][0]["progress"] == 0.0
    assert otra["people"] == []
    anonimo = cliente_de(None)
    assert anonimo.get("/api/participacion").status_code == 401
    lectura = anonimo.get(
        "/api/participacion", headers={"Authorization": f"Bearer {TOKEN_LECTURA}"}
    )
    assert lectura.status_code == 200
    assert lectura.json()["projects"][0]["id"] == "principal"
    falso = anonimo.get("/api/participacion", headers={"Authorization": "Bearer otro"})
    assert falso.status_code == 401
