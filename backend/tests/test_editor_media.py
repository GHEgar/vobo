import pytest

from app.services import contenido_media
from tests.apoyo_contenido import MP4, PNG, WEBP, seccion_nueva, versiones
from tests.conftest import TOKEN_LECTURA

RUTA = "/api/editor/procedimientos/entrar-a-la-tienda"


@pytest.fixture
def editor(en_base, cliente_de):
    return cliente_de("administracion")


def _subir(cliente, nombre: str, contenido: bytes, ruta: str = RUTA):
    return cliente.put(
        f"{ruta}/media", files={"archivo": (nombre, contenido, "application/octet-stream")}
    )


def _procedimiento(cliente, procedimiento_id: str) -> dict:
    return next(
        p
        for p in cliente.get("/api/contenido").json()["procedimientos"]
        if p["id"] == procedimiento_id
    )


def test_sube_y_reemplaza_una_animacion(editor) -> None:
    subida = _subir(editor, "entrar.webp", WEBP)
    assert subida.status_code == 200
    assert subida.json()["media"]["mime"] == "image/webp"
    assert (contenido_media.carpeta() / "entrar-a-la-tienda.webp").read_bytes() == WEBP
    assert _procedimiento(editor, "entrar-a-la-tienda")["url"].startswith(
        "/media/entrar-a-la-tienda.webp?v="
    )
    reemplazo = _subir(editor, "entrar.mp4", MP4)
    assert reemplazo.json()["media"]["archivo"] == "entrar-a-la-tienda.mp4"
    assert not (contenido_media.carpeta() / "entrar-a-la-tienda.webp").exists()
    acciones = [
        v["accion"]
        for v in editor.get("/api/editor/historial/procedimiento/entrar-a-la-tienda").json()
    ]
    assert acciones[:2] == ["reemplazar", "subir"]
    assert editor.delete(f"{RUTA}/media").json()["media"] is None
    assert not (contenido_media.carpeta() / "entrar-a-la-tienda.mp4").exists()
    assert _procedimiento(editor, "entrar-a-la-tienda")["url"] is None


@pytest.mark.parametrize(
    ("nombre", "contenido"),
    [
        ("falsa.webp", b"esto no es una imagen"),
        ("vacia.webp", b""),
        ("png.gif", PNG),
        ("enorme.webp", WEBP + b"\x00" * contenido_media.MAX_BYTES),
    ],
)
def test_rechaza_archivos_que_no_son_media(editor, nombre: str, contenido: bytes) -> None:
    assert _subir(editor, nombre, contenido).status_code == 422
    assert not any(contenido_media.carpeta().glob("entrar-a-la-tienda.*"))


def test_detecta_los_tipos_por_contenido() -> None:
    webm = b"\x1a\x45\xdf\xa3\x9f\x42\x86\x81\x01\x42\x82\x84webm" + b"\x00" * 16
    assert contenido_media.detectar(webm) == ("webm", "video/webm")
    assert contenido_media.detectar(b"GIF89a" + b"\x00" * 8) == ("gif", "image/gif")
    assert contenido_media.detectar(b"\xff\xd8\xff\xe0" + b"\x00" * 8) == ("jpg", "image/jpeg")
    assert contenido_media.detectar(PNG) == ("png", "image/png")
    assert contenido_media.detectar(MP4) == ("mp4", "video/mp4")
    assert contenido_media.detectar(b"<svg></svg>") is None


def test_crud_de_procedimientos(editor) -> None:
    nuevo = {
        "id": "pagar",
        "titulo": "Pagar",
        "descripcion": "Cómo pagar",
        "pasos": ["Abrir", "Pagar"],
    }
    assert editor.post("/api/editor/procedimientos", json={"datos": nuevo}).status_code == 201
    repetido = editor.post("/api/editor/procedimientos", json={"datos": nuevo})
    assert repetido.status_code == 422
    malo = editor.post(
        "/api/editor/procedimientos", json={"datos": {**nuevo, "id": "x", "pasos": "uno"}}
    )
    assert malo.json()["detail"][0]["loc"] == ["pasos"]
    cambiado = editor.put(
        "/api/editor/procedimientos/pagar", json={"datos": {**nuevo, "titulo": "Pagar ya"}}
    )
    assert cambiado.json()["datos"]["titulo"] == "Pagar ya"
    assert _procedimiento(editor, "pagar")["titulo"] == "Pagar ya"
    assert editor.delete("/api/editor/procedimientos/pagar").status_code == 204
    usado = editor.delete(RUTA)
    assert usado.status_code == 409
    assert "Lo usan las secciones" in usado.json()["detail"]
    lista = {p["id"]: p for p in editor.get("/api/editor/procedimientos").json()}
    assert lista["entrar-a-la-tienda"]["usos"]


def test_exportar_e_importar_no_cambia_nada(editor) -> None:
    _subir(editor, "entrar.webp", WEBP)
    editor.post("/api/editor/secciones", json={"datos": seccion_nueva()})
    antes = editor.get("/api/contenido").json()
    exportado = editor.get("/api/contenido/exportar.zip")
    assert exportado.headers["content-type"] == "application/zip"
    conteo = versiones()
    archivo = {"archivo": ("contenido.zip", exportado.content, "application/zip")}
    resumen = editor.post("/api/editor/importar?confirmar=true", files=archivo).json()
    assert resumen["sin_cambios"] is True
    assert resumen["aplicado"] is False
    assert versiones() == conteo
    assert editor.get("/api/contenido").json() == antes
    assert editor.get("/api/contenido/exportar.zip").content == exportado.content


def test_el_token_de_lectura_exporta(en_base, cliente_de) -> None:
    lectura = cliente_de(None)
    respuesta = lectura.get(
        "/api/contenido/exportar.zip", headers={"Authorization": f"Bearer {TOKEN_LECTURA}"}
    )
    assert respuesta.status_code == 200
    assert cliente_de("validador").get("/api/contenido/exportar.zip").status_code == 403
