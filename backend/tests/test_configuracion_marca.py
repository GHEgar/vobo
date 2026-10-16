from pathlib import Path

import pytest

from app.core.config import settings

RUTA = "/api/admin/configuracion/marca"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
WEBP = b"RIFF\x00\x00\x00\x00WEBPVP8 " + b"\x00" * 32
SVG = b'<?xml version="1.0"?>\n<svg xmlns="http://www.w3.org/2000/svg"><rect width="4"/></svg>'


@pytest.fixture
def admin(cliente_de, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "marca_dir", str(tmp_path / "marca"))
    return cliente_de("administracion")


def _subir(cliente, ranura: str, contenido: bytes, nombre: str = "logo.bin"):
    return cliente.put(f"{RUTA}/{ranura}", files={"archivo": (nombre, contenido)})


def test_sube_logo_y_se_sirve_con_cache_por_huella(admin, cliente_de) -> None:
    estado = _subir(admin, "logo_claro", PNG).json()
    url = estado["marca"]["logo_claro"]["url"]
    assert url.startswith("/api/instancia/marca/logo_claro.png?v=")
    publico = cliente_de(None)
    logo = publico.get("/api/instancia").json()["logo"]
    assert logo["claro"] == url
    assert logo["oscuro"] == url
    servido = publico.get(url)
    assert servido.status_code == 200
    assert servido.content == PNG
    assert servido.headers["content-type"] == "image/png"
    assert "immutable" in servido.headers["cache-control"]
    viejo = publico.get("/api/instancia/marca/logo_claro.png?v=otra")
    assert viejo.headers["cache-control"] == "no-cache"
    assert publico.get("/api/instancia/marca/logo_oscuro.png").status_code == 404
    assert publico.get("/api/instancia/marca/..%2Fsecreto").status_code == 404


def test_reemplazar_cambia_la_huella_y_borrar_vuelve_a_los_archivos(admin, cliente_de) -> None:
    primera = _subir(admin, "favicon", PNG).json()["marca"]["favicon"]
    segunda = _subir(admin, "favicon", WEBP).json()["marca"]["favicon"]
    assert segunda["archivo"] == "favicon.webp"
    assert segunda["url"] != primera["url"]
    assert not (Path(settings.marca_dir) / "favicon.png").exists()
    assert cliente_de(None).get("/api/instancia").json()["favicon"] == segunda["url"]
    assert admin.delete(f"{RUTA}/favicon").json()["marca"] == {}
    assert cliente_de(None).get("/api/instancia").json()["favicon"] == "/favicon.svg"
    assert not (Path(settings.marca_dir) / "favicon.webp").exists()


def test_svg_limpio_se_sirve_con_csp_estricta(admin, cliente_de) -> None:
    url = _subir(admin, "logo_oscuro", SVG).json()["marca"]["logo_oscuro"]["url"]
    servido = cliente_de(None).get(url)
    assert servido.headers["content-type"].startswith("image/svg+xml")
    assert "sandbox" in servido.headers["content-security-policy"]
    assert servido.headers["x-content-type-options"] == "nosniff"


@pytest.mark.parametrize(
    "contenido",
    [
        b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>',
        b'<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"></svg>',
        b'<svg xmlns="http://www.w3.org/2000/svg"><rect/onclick="x()"/></svg>',
        b'<svg xmlns="http://www.w3.org/2000/svg"><a href="javascript:alert(1)">x</a></svg>',
        b'<svg xmlns="http://www.w3.org/2000/svg"><a href="java\nscript:x">x</a></svg>',
        b'<svg xmlns="http://www.w3.org/2000/svg"><a href="&#106;avascript:x">x</a></svg>',
        b'<svg xmlns="http://www.w3.org/2000/svg"><image href="data:image/png;base64,AA"/></svg>',
        b'<svg xmlns="http://www.w3.org/2000/svg"><foreignObject></foreignObject></svg>',
    ],
)
def test_rechaza_svg_malicioso(admin, contenido: bytes) -> None:
    respuesta = _subir(admin, "logo_claro", contenido, "logo.svg")
    assert respuesta.status_code == 422
    assert not (Path(settings.marca_dir) / "logo_claro.svg").exists()


@pytest.mark.parametrize(
    "contenido",
    [
        b"",
        b"GIF89a" + b"\x00" * 16,
        b"\xff\xd8\xff" + b"\x00" * 16,
        b"<html><svg></svg></html>",
        b"texto cualquiera",
        PNG + b"\x00" * (2 * 1024 * 1024),
    ],
)
def test_rechaza_lo_que_no_es_png_svg_ni_webp(admin, contenido: bytes) -> None:
    assert _subir(admin, "logo_claro", contenido).status_code == 422


def test_ranura_desconocida(admin) -> None:
    assert _subir(admin, "portada", PNG).status_code == 422
