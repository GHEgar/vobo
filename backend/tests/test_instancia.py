from pathlib import Path

import pytest

from app.core.config import settings
from app.services import contenido
from tests.conftest import CONTENIDO


@pytest.fixture
def raiz(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / "secciones").mkdir()
    monkeypatch.setattr(settings, "contenido_dir", str(tmp_path))
    return tmp_path


def test_sin_sesion_devuelve_la_instancia_de_ejemplo(cliente_de) -> None:
    respuesta = cliente_de(None).get("/api/instancia")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert set(datos) == {"nombre", "descripcion", "proyectos"}
    assert datos["nombre"] == "Validaciones"
    assert {"clave": "general", "nombre": "General"} in datos["proyectos"]


def test_sin_archivo_usa_los_valores_por_omision(cliente_de, raiz) -> None:
    assert cliente_de(None).get("/api/instancia").json() == {
        "nombre": "Validaciones",
        "descripcion": "",
        "proyectos": [],
    }


def test_campos_faltantes_toman_su_valor_por_omision(cliente_de, raiz) -> None:
    (raiz / "instancia.yaml").write_text("nombre: Pruebas QA\ndescripcion:\n", encoding="utf-8")
    assert cliente_de(None).get("/api/instancia").json() == {
        "nombre": "Pruebas QA",
        "descripcion": "",
        "proyectos": [],
    }


def test_un_yaml_roto_no_tumba_la_api(cliente_de, raiz) -> None:
    (raiz / "instancia.yaml").write_text("nombre: [roto\n", encoding="utf-8")
    respuesta = cliente_de(None).get("/api/instancia")
    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "Validaciones"
    errores = contenido.cargar(raiz).respuesta.errores
    assert any(e.startswith("instancia.yaml") for e in errores)


def test_proyectos_invalidos_se_reportan(raiz) -> None:
    (raiz / "instancia.yaml").write_text("proyectos:\n  - clave: x\n", encoding="utf-8")
    actual = contenido.cargar(raiz)
    assert actual.instancia.proyectos == []
    assert any(e.startswith("instancia.yaml") for e in actual.respuesta.errores)


def test_se_recarga_en_caliente(cliente_de, raiz) -> None:
    import os

    archivo = raiz / "instancia.yaml"
    archivo.write_text("nombre: Uno\n", encoding="utf-8")
    cliente = cliente_de(None)
    assert cliente.get("/api/instancia").json()["nombre"] == "Uno"
    archivo.write_text("nombre: Dos\n", encoding="utf-8")
    os.utime(archivo, ns=(1, archivo.stat().st_mtime_ns + 10_000_000))
    assert cliente.get("/api/instancia").json()["nombre"] == "Dos"


def test_el_ejemplo_cubre_los_proyectos_de_sus_secciones() -> None:
    actual = contenido.cargar(CONTENIDO)
    claves = {p.clave for p in actual.instancia.proyectos}
    assert {s.sistema for s in actual.respuesta.secciones} <= claves
