import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.time import como_utc, utcnow
from app.models.contenido import ContenidoMedia
from app.services import contenido_versiones as versiones
from app.services import proyectos
from app.services.contenido import PREFIJO_MEDIA
from app.services.evidencias import tipo_de_imagen

MAX_BYTES = 20 * 1024 * 1024
EXTENSIONES = {
    "webp": "image/webp",
    "gif": "image/gif",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "mp4": "video/mp4",
    "webm": "video/webm",
}
PREFERENCIA = ("webp", "gif", "png", "jpg", "mp4", "webm")
NOMBRE = re.compile(r"^(?P<id>[a-z0-9][a-z0-9-]{0,119})\.(?P<ext>[a-z0-9]{2,5})$")


@dataclass(frozen=True)
class Archivo:
    contenido: bytes
    extension: str
    mime: str

    @property
    def huella(self) -> str:
        return hashlib.sha256(self.contenido).hexdigest()


def _rechazo(detalle: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=detalle)


def detectar(contenido: bytes) -> tuple[str, str] | None:
    imagen = tipo_de_imagen(contenido)
    if imagen is not None:
        return imagen[1], imagen[0]
    if contenido[4:8] == b"ftyp":
        return "mp4", "video/mp4"
    if contenido[:4] == b"\x1a\x45\xdf\xa3" and b"webm" in contenido[:64]:
        return "webm", "video/webm"
    return None


def validar(contenido: bytes, nombre: str = "") -> Archivo:
    if not contenido:
        raise _rechazo(f"{nombre or 'El archivo'} está vacío")
    if len(contenido) > MAX_BYTES:
        raise _rechazo(f"{nombre or 'El archivo'} pesa más de 20 MB")
    tipo = detectar(contenido)
    if tipo is None:
        raise _rechazo(
            f"{nombre or 'El archivo'} no es WebP, GIF, PNG, JPEG, MP4 ni WebM por su contenido"
        )
    extension, mime = tipo
    declarada = nombre.rsplit(".", 1)[-1].lower() if "." in nombre else ""
    if declarada and EXTENSIONES.get(declarada) not in {None, mime}:
        raise _rechazo(f"{nombre} dice ser .{declarada} pero su contenido es {mime}")
    return Archivo(contenido=contenido, extension=extension, mime=mime)


def carpeta() -> Path:
    return Path(settings.media_dir)


def url_de(media: ContenidoMedia) -> str:
    version = int(como_utc(media.subido).timestamp())
    return f"{PREFIJO_MEDIA}/{media.archivo}?v={version}"


def urls(db: Session, proyecto_id: int) -> dict[str, str]:
    consulta = select(ContenidoMedia).where(ContenidoMedia.proyecto_id == proyecto_id)
    return {m.procedimiento_id: url_de(m) for m in db.scalars(consulta)}


def de(db: Session, proyecto_id: int, procedimiento_id: str) -> ContenidoMedia | None:
    return db.get(
        ContenidoMedia, {"proyecto_id": proyecto_id, "procedimiento_id": procedimiento_id}
    )


def metadatos(media: ContenidoMedia | None) -> dict | None:
    if media is None:
        return None
    return {
        "archivo": media.archivo,
        "mime": media.mime,
        "tamano": media.tamano,
        "huella": media.huella,
    }


def _escribir(nombre: str, contenido: bytes) -> None:
    destino = carpeta() / nombre
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_name(f".{destino.name}.subiendo")
    temporal.write_bytes(contenido)
    os.replace(temporal, destino)


def _quitar(nombre: str) -> None:
    (carpeta() / nombre).unlink(missing_ok=True)


def guardar(
    db: Session, proyecto_id: int, procedimiento_id: str, archivo: Archivo, autor: str
) -> ContenidoMedia:
    actual = de(db, proyecto_id, procedimiento_id)
    if actual is not None and actual.huella == archivo.huella:
        return actual
    nombre = f"{proyectos.carpeta_media(proyecto_id, db)}{procedimiento_id}.{archivo.extension}"
    _escribir(nombre, archivo.contenido)
    anterior = metadatos(actual)
    if actual is None:
        actual = ContenidoMedia(proyecto_id=proyecto_id, procedimiento_id=procedimiento_id)
        db.add(actual)
    elif actual.archivo != nombre:
        _quitar(actual.archivo)
    actual.archivo = nombre
    actual.mime = archivo.mime
    actual.tamano = len(archivo.contenido)
    actual.huella = archivo.huella
    actual.subido = utcnow()
    actual.autor_email = autor
    accion = "reemplazar" if anterior else "subir"
    versiones.registrar(db, proyecto_id, "media", procedimiento_id, accion, anterior, autor)
    return actual


def borrar(db: Session, proyecto_id: int, procedimiento_id: str, autor: str) -> None:
    actual = de(db, proyecto_id, procedimiento_id)
    if actual is None:
        return
    versiones.registrar(
        db, proyecto_id, "media", procedimiento_id, "borrar", metadatos(actual), autor
    )
    _quitar(actual.archivo)
    db.delete(actual)


def quitar_archivos(nombres: list[str]) -> None:
    for nombre in nombres:
        _quitar(nombre)


def leer(media: ContenidoMedia) -> bytes | None:
    ruta = carpeta() / media.archivo
    return ruta.read_bytes() if ruta.is_file() else None
