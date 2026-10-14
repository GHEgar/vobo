from pathlib import Path

from app.services import contenido
from tests.conftest import TOKEN_LECTURA


def test_seccion_sin_herramientas_usa_general(tmp_path: Path) -> None:
    (tmp_path / "secciones").mkdir()
    (tmp_path / "secciones" / "10.yaml").write_text(
        "id: s\ntitulo: S\nsistema: x\ncasos:\n  - id: C-1\n    familia: C\n    titulo: T\n"
        "    pasos:\n      - texto: Haz algo.\n    esperado: Pasa algo.\n    severidad: baja\n",
        encoding="utf-8",
    )
    actual = contenido.cargar(tmp_path)
    assert actual.respuesta.secciones[0].herramientas[0].id == "general"
    assert actual.casos["C-1"].caso.herramienta == "general"
    assert actual.herramientas == {}


def test_herramientas_excluyen_general_y_guardan_decision(cliente_de, ronda_id) -> None:
    coordinacion = cliente_de("coordinacion")
    lista = coordinacion.get(f"/api/herramientas?ronda={ronda_id}").json()
    assert all(h["id"] != "general" for h in lista)
    assert (
        coordinacion.put(
            "/api/decisiones/general", json={"ronda_id": ronda_id, "decision": "aplazar"}
        ).status_code
        == 404
    )
    if not lista:
        return
    herramienta = lista[0]["id"]
    assert lista[0]["sugerencia"] == "sin_probar"
    respuesta = coordinacion.put(
        f"/api/decisiones/{herramienta}",
        json={"ronda_id": ronda_id, "decision": "aplazar", "motivo": "Falta probar"},
    )
    assert respuesta.status_code == 200
    validador = cliente_de("validador")
    assert (
        validador.put(
            f"/api/decisiones/{herramienta}", json={"ronda_id": ronda_id, "decision": "desplegar"}
        ).status_code
        == 403
    )
    cabecera = {"Authorization": f"Bearer {TOKEN_LECTURA}"}
    leidas = cliente_de(None).get(f"/api/herramientas?ronda={ronda_id}", headers=cabecera).json()
    elegida = next(h for h in leidas if h["id"] == herramienta)
    assert elegida["decision"]["decision"] == "aplazar"
    tablero = cliente_de(None).get(f"/api/tablero?ronda={ronda_id}", headers=cabecera).json()
    assert tablero["decisiones"][0]["herramienta_id"] == herramienta
