import hashlib
import html
import os
import re
from pathlib import Path

from fastapi import HTTPException, status

from app.core.config import settings
from app.services.evidencias import tipo_de_imagen

MAX_BYTES = 2 * 1024 * 1024
PREFIJO = "/api/instancia/marca"
RASTER = {"image/png": "png", "image/webp": "webp"}
MIME_SVG = "image/svg+xml"
CSP_SVG = "default-src 'none'; style-src 'unsafe-inline'; img-src 'self'; sandbox"
NOMBRE = re.compile(r"^(?P<ranura>logo_claro|logo_oscuro|favicon)\.(?P<ext>png|webp|svg)$")
INICIO_SVG = re.compile(
    r"^﻿?\s*(<\?xml[^>]*\?>\s*)?((<!--.*?-->|<!doctype[^>\[]*>)\s*)*<svg[\s>]",
    re.IGNORECASE | re.DOTALL,
)
MANEJADOR = re.compile(r"[\s/\"']on[a-z]+\s*=", re.IGNORECASE)
PELIGROSOS = ("<script", "javascript:", "vbscript:", "data:", "<!entity", "<foreignobject")
MIMES = {"png": "image/png", "webp": "image/webp", "svg": MIME_SVG}


def _rechazo(detalle: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=detalle)


def _svg_seguro(contenido: bytes) -> bool:
    try:
        texto = contenido.decode("utf-8")
    except UnicodeDecodeError:
        return False
    if not INICIO_SVG.match(texto):
        return False
    plano = html.unescape(texto)
    compacto = re.sub(r"\s+", "", plano).lower()
    if any(p in compacto for p in PELIGROSOS):
        raise _rechazo("El SVG trae scripts, manejadores de eventos o enlaces no permitidos")
    if MANEJADOR.search(plano):
        raise _rechazo("El SVG trae scripts, manejadores de eventos o enlaces no permitidos")
    return True


def validar(contenido: bytes) -> tuple[str, str]:
    if not contenido:
        raise _rechazo("El archivo está vacío")
    if len(contenido) > MAX_BYTES:
        raise _rechazo("El archivo pesa más de 2 MB")
    imagen = tipo_de_imagen(contenido)
    if imagen is not None and imagen[0] in RASTER:
        return imagen[0], RASTER[imagen[0]]
    if imagen is None and _svg_seguro(contenido):
        return MIME_SVG, "svg"
    raise _rechazo("Solo se aceptan PNG, SVG o WebP, reconocidos por su contenido")


def carpeta() -> Path:
    return Path(settings.marca_dir)


def huella(contenido: bytes) -> str:
    return hashlib.sha256(contenido).hexdigest()


def url(archivo: str, firma: str) -> str:
    return f"{PREFIJO}/{archivo}?v={firma[:16]}"


def escribir(nombre: str, contenido: bytes) -> None:
    destino = carpeta() / nombre
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_name(f".{nombre}.subiendo")
    temporal.write_bytes(contenido)
    os.replace(temporal, destino)


def quitar(nombre: str) -> None:
    (carpeta() / nombre).unlink(missing_ok=True)


def leer(nombre: str) -> tuple[bytes, str] | None:
    coincide = NOMBRE.match(nombre)
    if coincide is None:
        return None
    ruta = carpeta() / nombre
    if not ruta.is_file():
        return None
    return ruta.read_bytes(), MIMES[coincide["ext"]]


def cabeceras(mime: str, vigente: bool) -> dict[str, str]:
    encabezados = {
        "Cache-Control": "public, max-age=31536000, immutable" if vigente else "no-cache",
        "X-Content-Type-Options": "nosniff",
    }
    if mime == MIME_SVG:
        encabezados["Content-Security-Policy"] = CSP_SVG
    return encabezados
