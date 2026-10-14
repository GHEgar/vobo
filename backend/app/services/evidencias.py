import secrets
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

MAX_BYTES = 5 * 1024 * 1024
MAX_ARCHIVOS = 5
FIRMAS = (
    (b"\x89PNG\r\n\x1a\n", "image/png", "png"),
    (b"\xff\xd8\xff", "image/jpeg", "jpg"),
    (b"GIF87a", "image/gif", "gif"),
    (b"GIF89a", "image/gif", "gif"),
)


def _tipo(contenido: bytes) -> tuple[str, str] | None:
    if contenido[:4] == b"RIFF" and contenido[8:12] == b"WEBP":
        return "image/webp", "webp"
    for firma, mime, extension in FIRMAS:
        if contenido.startswith(firma):
            return mime, extension
    return None


def _rechazo(detalle: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detalle)


async def leer(archivos: list[UploadFile]) -> list[tuple[bytes, str, str]]:
    if len(archivos) > MAX_ARCHIVOS:
        raise _rechazo(f"Se aceptan como máximo {MAX_ARCHIVOS} imágenes")
    leidos = []
    for archivo in archivos:
        contenido = await archivo.read(MAX_BYTES + 1)
        if len(contenido) > MAX_BYTES:
            raise _rechazo(f"{archivo.filename} pesa más de 5 MB")
        tipo = _tipo(contenido)
        if tipo is None:
            raise _rechazo(f"{archivo.filename} no es una imagen PNG, JPG, GIF o WebP")
        leidos.append((contenido, *tipo))
    return leidos


def guardar(falla_id: int, contenido: bytes, extension: str) -> str:
    relativa = Path(str(falla_id)) / f"{secrets.token_hex(12)}.{extension}"
    destino = Path(settings.evidencias_dir) / relativa
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(contenido)
    return str(relativa)


def ruta_absoluta(relativa: str) -> Path:
    raiz = Path(settings.evidencias_dir).resolve()
    ruta = (raiz / relativa).resolve()
    if raiz not in ruta.parents:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidencia no encontrada")
    return ruta
