from collections import Counter

from app.services.herramientas import sugerir


def test_regla_de_recomendacion() -> None:
    assert sugerir(["pasa", "pendiente"], Counter())[0] == "sin_probar"
    assert sugerir([], Counter())[0] == "sin_probar"
    assert sugerir(["pasa", "falla"], Counter({"alta": 1}))[0] == "aplazar"
    assert sugerir(["pasa", "no_pude", "no_pude"], Counter())[0] == "aplazar"
    assert sugerir(["pasa"] * 4 + ["no_pude"], Counter())[0] == "desplegar"
    assert sugerir(["pasa", "falla"], Counter({"media": 1}))[0] == "desplegar_con_aviso"
    recomendacion, motivo = sugerir(["pasa", "pasa"], Counter())
    assert recomendacion == "desplegar"
    assert motivo


def test_recomendacion_con_aviso_se_guarda(cliente_de, ronda_id) -> None:
    coordinacion = cliente_de("coordinacion")
    herramienta = coordinacion.get(f"/api/herramientas?ronda={ronda_id}").json()[0]["id"]
    respuesta = coordinacion.put(
        f"/api/decisiones/{herramienta}",
        json={"ronda_id": ronda_id, "decision": "desplegar_con_aviso", "motivo": "Solo una media"},
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["decision"] == "desplegar_con_aviso"
