import io
import zipfile
from pathlib import Path

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.contenido import ContenidoMedia, ContenidoProcedimiento, ContenidoSeccion
from app.services import contenido_media as medias
from app.services import instancia as instancias

FECHA_FIJA = (2000, 1, 1, 0, 0, 0)


def _yaml(datos: object) -> bytes:
    return yaml.safe_dump(datos, allow_unicode=True, sort_keys=False, width=100).encode("utf-8")


def _agregar(archivo: zipfile.ZipFile, nombre: str, contenido: bytes) -> None:
    info = zipfile.ZipInfo(nombre, date_time=FECHA_FIJA)
    info.compress_type = zipfile.ZIP_DEFLATED
    archivo.writestr(info, contenido)


def _de_base(db: Session, proyecto_id: int) -> list[tuple[str, bytes]]:
    entradas = []
    secciones = select(ContenidoSeccion).where(ContenidoSeccion.proyecto_id == proyecto_id)
    for fila in db.scalars(secciones.order_by(ContenidoSeccion.id)):
        entradas.append((f"secciones/{fila.id}.yaml", _yaml(fila.datos)))
    orden = (ContenidoProcedimiento.orden, ContenidoProcedimiento.id)
    consulta = select(ContenidoProcedimiento).where(
        ContenidoProcedimiento.proyecto_id == proyecto_id
    )
    procedimientos = [f.datos for f in db.scalars(consulta.order_by(*orden))]
    if procedimientos:
        entradas.append(("procedimientos.yaml", _yaml(procedimientos)))
    propias = select(ContenidoMedia).where(ContenidoMedia.proyecto_id == proyecto_id)
    for media in db.scalars(propias.order_by(ContenidoMedia.archivo)):
        contenido = medias.leer(media)
        if contenido is not None:
            entradas.append((f"media/{Path(media.archivo).name}", contenido))
    instancia = instancias.ruta_de(Path(settings.contenido_dir))
    if instancia.is_file():
        entradas.append((instancia.name, instancia.read_bytes()))
    return entradas


def _de_archivos(raiz: Path) -> list[tuple[str, bytes]]:
    rutas = [
        *sorted(raiz.glob("secciones/*.yaml")),
        *sorted(raiz.glob("procedimientos*.yaml")),
        *sorted(p for p in raiz.glob("media/*") if p.is_file()),
    ]
    instancia = instancias.ruta_de(raiz)
    if instancia.is_file():
        rutas.append(instancia)
    return [(r.relative_to(raiz).as_posix(), r.read_bytes()) for r in rutas]


def exportar(db: Session, proyecto_id: int) -> bytes:
    if settings.contenido_en_base:
        entradas = _de_base(db, proyecto_id)
    else:
        entradas = _de_archivos(Path(settings.contenido_dir))
    salida = io.BytesIO()
    with zipfile.ZipFile(salida, "w") as archivo:
        for nombre, contenido in entradas:
            _agregar(archivo, nombre, contenido)
    return salida.getvalue()
