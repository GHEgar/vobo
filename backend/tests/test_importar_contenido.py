import pytest
import yaml

from tests.apoyo_contenido import WEBP, armar_zip, con_resultado, leer_zip, versiones
from tests.conftest import CONTENIDO


@pytest.fixture
def editor(en_base, cliente_de):
    return cliente_de("administracion")


def _importar(cliente, contenido: bytes, confirmar: bool):
    archivo = {"archivo": ("contenido.zip", contenido, "application/zip")}
    return cliente.post(f"/api/editor/importar?confirmar={str(confirmar).lower()}", files=archivo)


def _modificado(cliente) -> bytes:
    entradas = leer_zip(cliente.get("/api/contenido/exportar.zip").content)
    del entradas["secciones/pedidos.yaml"]
    catalogo = yaml.safe_load(entradas["secciones/catalogo.yaml"])
    catalogo["titulo"] = "Catálogo renovado"
    entradas["secciones/catalogo.yaml"] = yaml.safe_dump(catalogo, allow_unicode=True).encode()
    entradas["media/ventana-incognito.webp"] = WEBP
    return armar_zip({f"exportado/{k}": v for k, v in entradas.items()})


def test_importar_muestra_el_plan_y_aplica_al_confirmar(editor) -> None:
    contenido = _modificado(editor)
    conteo = versiones()
    plan = _importar(editor, contenido, confirmar=False).json()
    assert plan["aplicado"] is False
    assert plan["secciones"] == {"crear": [], "actualizar": ["catalogo"], "borrar": ["pedidos"]}
    assert plan["media"]["crear"] == ["ventana-incognito"]
    assert versiones() == conteo
    aplicado = _importar(editor, contenido, confirmar=True).json()
    assert aplicado["aplicado"] is True
    secciones = {s["id"]: s for s in editor.get("/api/contenido").json()["secciones"]}
    assert "pedidos" not in secciones
    assert secciones["catalogo"]["titulo"] == "Catálogo renovado"
    assert versiones() == conteo + 3
    borrada = editor.get("/api/editor/historial/seccion/pedidos").json()[0]
    assert borrada["accion"] == "borrar"
    assert editor.post(f"/api/editor/historial/{borrada['id']}/restaurar").status_code == 204


def test_importar_no_quita_casos_con_resultados(editor, ronda_id) -> None:
    con_resultado(ronda_id, "C-PED-01")
    contenido = _modificado(editor)
    resumen = _importar(editor, contenido, confirmar=True).json()
    assert resumen["aplicado"] is False
    assert any("C-PED-01" in b for b in resumen["bloqueos"])
    assert "pedidos" in [s["id"] for s in editor.get("/api/contenido").json()["secciones"]]


def test_importar_rechaza_un_paquete_invalido(editor) -> None:
    assert _importar(editor, b"no es zip", confirmar=True).status_code == 422
    roto = armar_zip({"secciones/a.yaml": b"id: [roto", "media/x.webp": b"falso"})
    errores = _importar(editor, roto, confirmar=True).json()["detail"]
    assert len(errores) == 2
    duplicado = (CONTENIDO / "secciones" / "10-primeros-pasos.yaml").read_bytes()
    repetidos = armar_zip({"secciones/a.yaml": duplicado, "secciones/b.yaml": duplicado})
    assert _importar(editor, repetidos, confirmar=True).status_code == 422


def test_con_archivos_exporta_la_carpeta(cliente_de) -> None:
    entradas = leer_zip(cliente_de("administracion").get("/api/contenido/exportar.zip").content)
    assert "secciones/10-primeros-pasos.yaml" in entradas
    assert "procedimientos.yaml" in entradas
    assert entradas["instancia.yaml"] == (CONTENIDO / "instancia.yaml").read_bytes()
