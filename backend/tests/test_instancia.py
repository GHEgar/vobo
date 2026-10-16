from pathlib import Path

import pytest

from app.core.config import settings
from app.services import contenido
from tests.conftest import CONTENIDO

POR_OMISION = {
    "producto": "VoBo",
    "nombre": "",
    "descripcion": "",
    "logo": None,
    "favicon": "/favicon.svg",
    "color_tema": "#1F4E79",
    "entrada": {"titulo": "", "mensaje": ""},
    "proyectos": [],
    "sistemas": [],
    "proyecto": {
        "clave": "principal",
        "nombre": "Principal",
        "color_nombre": None,
        "por_omision": True,
    },
}


@pytest.fixture
def raiz(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / "secciones").mkdir()
    monkeypatch.setattr(settings, "contenido_dir", str(tmp_path))
    return tmp_path


def test_sin_sesion_devuelve_la_instancia_de_ejemplo(cliente_de) -> None:
    respuesta = cliente_de(None).get("/api/instancia")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert set(datos) == set(POR_OMISION)
    assert datos["producto"] == "Visto Bueno"
    assert datos["nombre"] == "Tienda en línea"
    assert datos["logo"] == {
        "claro": "/tema/logo.svg",
        "oscuro": "/tema/logo-oscuro.svg",
        "alt": "Visto Bueno",
    }
    assert datos["color_tema"] == "#2E6B3F"
    assert datos["entrada"]["titulo"]
    assert {"clave": "general", "nombre": "General"} in datos["proyectos"]
    assert datos["sistemas"] == datos["proyectos"]


def test_acepta_sistemas_como_clave_nueva(cliente_de, raiz) -> None:
    (raiz / "instancia.yaml").write_text(
        "sistemas:\n  - clave: web\n    nombre: Sitio web\n", encoding="utf-8"
    )
    datos = cliente_de(None).get("/api/instancia").json()
    assert datos["proyectos"] == datos["sistemas"] == [{"clave": "web", "nombre": "Sitio web"}]


def test_sin_archivo_usa_los_valores_por_omision(cliente_de, raiz) -> None:
    assert cliente_de(None).get("/api/instancia").json() == POR_OMISION


def test_campos_faltantes_toman_su_valor_por_omision(cliente_de, raiz) -> None:
    (raiz / "instancia.yaml").write_text("nombre: Pruebas QA\ndescripcion:\n", encoding="utf-8")
    assert cliente_de(None).get("/api/instancia").json() == {**POR_OMISION, "nombre": "Pruebas QA"}


def test_un_yaml_roto_no_tumba_la_api(cliente_de, raiz) -> None:
    (raiz / "instancia.yaml").write_text("nombre: [roto\n", encoding="utf-8")
    respuesta = cliente_de(None).get("/api/instancia")
    assert respuesta.status_code == 200
    assert respuesta.json() == POR_OMISION
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


def test_la_marca_resuelve_rutas_del_tema(cliente_de, raiz) -> None:
    (raiz / "instancia.yaml").write_text(
        "producto: Revisión\n"
        "logo:\n  claro: marca/logo claro.svg\n  oscuro: ./marca/logo-oscuro.svg\n"
        "favicon: marca/icono.png\n"
        "color_tema: '#0b6e4f'\n"
        "entrada:\n  titulo: Hola\n",
        encoding="utf-8",
    )
    datos = cliente_de(None).get("/api/instancia").json()
    assert datos["producto"] == "Revisión"
    assert datos["logo"] == {
        "claro": "/tema/marca/logo%20claro.svg",
        "oscuro": "/tema/marca/logo-oscuro.svg",
        "alt": "Revisión",
    }
    assert datos["favicon"] == "/tema/marca/icono.png"
    assert datos["color_tema"] == "#0B6E4F"
    assert datos["entrada"] == {"titulo": "Hola", "mensaje": ""}


def test_sin_logo_oscuro_usa_el_claro(cliente_de, raiz) -> None:
    archivo = raiz / "instancia.yaml"
    archivo.write_text("logo:\n  claro: logo.svg\n  alt: Marca\n", encoding="utf-8")
    assert cliente_de(None).get("/api/instancia").json()["logo"] == {
        "claro": "/tema/logo.svg",
        "oscuro": "/tema/logo.svg",
        "alt": "Marca",
    }


@pytest.mark.parametrize(
    "ruta",
    [
        "../secreto.svg",
        "marca/../../fuera.svg",
        "/etc/logo.svg",
        "https://ejemplo.test/logo.svg",
        "data:image/svg+xml,<svg/>",
        "C:/logo.svg",
        "marca\\logo.svg",
        "logo.svg?v=1",
        "",
        ".",
    ],
)
def test_rutas_fuera_del_tema_se_rechazan(cliente_de, raiz, ruta: str) -> None:
    (raiz / "instancia.yaml").write_text(
        f"nombre: Sigue\nlogo:\n  claro: '{ruta}'\nfavicon: '{ruta}'\n", encoding="utf-8"
    )
    datos = cliente_de(None).get("/api/instancia").json()
    assert datos["nombre"] == "Sigue"
    assert datos["logo"] is None
    assert datos["favicon"] == "/favicon.svg"
    errores = contenido.cargar(raiz).respuesta.errores
    assert any(e.startswith("instancia.yaml") for e in errores)


@pytest.mark.parametrize("color", ["1F4E79", "#1F4E7", "#1F4E79FF", "#GGGGGG", "azul"])
def test_color_tema_invalido_se_reporta(cliente_de, raiz, color: str) -> None:
    archivo = raiz / "instancia.yaml"
    archivo.write_text(f"nombre: Sigue\ncolor_tema: '{color}'\n", encoding="utf-8")
    datos = cliente_de(None).get("/api/instancia").json()
    assert datos["nombre"] == "Sigue"
    assert datos["color_tema"] == "#1F4E79"
    assert any(e.startswith("instancia.yaml") for e in contenido.cargar(raiz).respuesta.errores)


def test_un_campo_de_marca_invalido_no_borra_los_proyectos(raiz) -> None:
    (raiz / "instancia.yaml").write_text(
        "color_tema: rojo\nproyectos:\n  - clave: a\n    nombre: A\n", encoding="utf-8"
    )
    actual = contenido.cargar(raiz)
    assert [p.clave for p in actual.instancia.proyectos] == ["a"]
    assert actual.instancia.color_tema == "#1F4E79"


def test_producto_vacio_toma_el_valor_por_omision(cliente_de, raiz) -> None:
    (raiz / "instancia.yaml").write_text("producto: '  '\n", encoding="utf-8")
    assert cliente_de(None).get("/api/instancia").json()["producto"] == "VoBo"


def test_color_nombre_del_archivo_va_a_la_hoja_y_lo_guardado_gana(cliente_de, raiz) -> None:
    (raiz / "instancia.yaml").write_text("color_nombre: '#336699'\n", encoding="utf-8")
    assert "--color-nombre: #336699;" in cliente_de(None).get("/api/instancia/tema.css").text
    admin = cliente_de("administracion")
    assert admin.get("/api/admin/configuracion").json()["archivos"]["colores"] == {
        "nombre": "#336699"
    }
    admin.put("/api/admin/configuracion", json={"colores": {"nombre": "#AA0000"}})
    hoja = cliente_de(None).get("/api/instancia/tema.css").text
    assert "--color-nombre: #AA0000;" in hoja
    assert "#336699" not in hoja
    admin.delete("/api/admin/configuracion/colores")
    assert "--color-nombre: #336699;" in cliente_de(None).get("/api/instancia/tema.css").text


@pytest.mark.parametrize("color", ["336699", "#33669", "naranja"])
def test_color_nombre_invalido_se_reporta_sin_romper_la_hoja(cliente_de, raiz, color: str) -> None:
    (raiz / "instancia.yaml").write_text(
        f"nombre: Sigue\ncolor_nombre: '{color}'\n", encoding="utf-8"
    )
    assert cliente_de(None).get("/api/instancia").json()["nombre"] == "Sigue"
    assert cliente_de(None).get("/api/instancia/tema.css").text == ""
    assert any(e.startswith("instancia.yaml") for e in contenido.cargar(raiz).respuesta.errores)
