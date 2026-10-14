import shutil
from pathlib import Path

import pytest

from app.core.config import settings
from tests.conftest import CONTENIDO

TECNICA = """id: prueba-tecnica
orden: 999
titulo: Sección técnica de prueba
sistema: infraestructura
audiencia: tecnica
casos:
  - id: T-PRUEBA-01
    familia: T
    titulo: El respaldo restaura
    pasos:
      - texto: Corre make restore.
    esperado: Restaura sin errores.
    severidad: alta
"""


@pytest.fixture(autouse=True)
def contenido_con_tecnica(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    shutil.copytree(CONTENIDO / "secciones", tmp_path / "secciones")
    for extra in (CONTENIDO).glob("procedimientos*.yaml"):
        shutil.copy(extra, tmp_path / extra.name)
    (tmp_path / "secciones" / "999-prueba-tecnica.yaml").write_text(TECNICA, encoding="utf-8")
    monkeypatch.setattr(settings, "contenido_dir", str(tmp_path))


def _mis(cliente, ronda_id) -> dict:
    return cliente.get(f"/api/mis-casos?ronda={ronda_id}").json()


def _marcar(cliente, ronda_id, caso="T-PRUEBA-01"):
    return cliente.put(f"/api/resultados/{caso}", json={"ronda_id": ronda_id, "estado": "pasa"})


def test_validador_no_ve_tecnica_por_omision(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    _marcar(validador, ronda_id)
    mis = _mis(validador, ronda_id)
    assert "prueba-tecnica" not in mis["secciones_visibles"]
    assert "primeros-pasos" in mis["secciones_visibles"]
    assert mis["ve_tecnico"] is False
    assert all(r["caso_id"] != "T-PRUEBA-01" for r in mis["resultados"])
    assert (
        validador.post(
            "/api/secciones/prueba-tecnica/resultado", data={"ronda_id": ronda_id, "estado": "pasa"}
        ).status_code
        == 403
    )


def test_tecnica_visible_si_esta_asignada(cliente_de, ronda_id) -> None:
    cliente_de("coordinacion").put(
        f"/api/rondas/{ronda_id}/asignaciones",
        json=[{"usuario_email": "validador@local.test", "seccion_id": "prueba-tecnica"}],
    )
    mis = _mis(cliente_de("validador"), ronda_id)
    assert mis["secciones_visibles"] == ["prueba-tecnica"]
    assert mis["ve_tecnico"] is True


def test_tecnica_visible_con_acceso_tecnico(cliente_de, ronda_id) -> None:
    cliente_de("coordinacion").put(
        "/api/accesos", json=[{"usuario_email": "validador@local.test", "paginas": ["tecnico"]}]
    )
    validador = cliente_de("validador")
    assert "tecnico" in validador.get("/api/auth/me").json()["usuario"]["paginas"]
    mis = _mis(validador, ronda_id)
    assert {"prueba-tecnica", "primeros-pasos"} <= set(mis["secciones_visibles"])
    assert _marcar(validador, ronda_id).status_code == 200
    assert any(r["caso_id"] == "T-PRUEBA-01" for r in _mis(validador, ronda_id)["resultados"])


def test_coordinacion_ve_tecnica_y_tablero_filtra(cliente_de, ronda_id) -> None:
    coordinacion = cliente_de("coordinacion")
    assert "prueba-tecnica" in _mis(coordinacion, ronda_id)["secciones_visibles"]
    _marcar(coordinacion, ronda_id)
    _marcar(cliente_de("validador"), ronda_id, "A-GEN-01")
    tecnico = coordinacion.get(f"/api/tablero?ronda={ronda_id}&audiencia=tecnica").json()
    assert "infraestructura" in tecnico["proyectos"]
    assert [p["email"] for p in tecnico["personas"]] == ["coordinacion@local.test"]
    celda_t = next(c for c in tecnico["personas"][0]["celdas"] if c["familia"] == "T")
    assert celda_t["hechos"] == 1
    assert celda_t["total"] >= 1
    funcional = coordinacion.get(f"/api/tablero?ronda={ronda_id}&audiencia=funcional").json()
    assert all(
        c["total"] == 0 for p in funcional["personas"] for c in p["celdas"] if c["familia"] == "T"
    )
