import logging
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy import Engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.time import utcnow
from app.models.contenido import (
    ContenidoMedia,
    ContenidoProcedimiento,
    ContenidoSeccion,
    ContenidoVersion,
)
from app.services import contenido_media as medias
from app.services import contenido_referencias as referencias
from app.services import contenido_versiones as versiones
from app.services import proyectos
from app.services.contenido_paquete import Paquete, de_directorio

AUTOR_INICIAL = "importacion-inicial"

logger = logging.getLogger("validacion.contenido")


@dataclass
class Cambios:
    crear: list[str] = field(default_factory=list)
    actualizar: list[str] = field(default_factory=list)
    borrar: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.crear) + len(self.actualizar) + len(self.borrar)


@dataclass
class Plan:
    secciones: Cambios
    procedimientos: Cambios
    media: Cambios
    bloqueos: list[str]

    @property
    def sin_cambios(self) -> bool:
        return not (self.secciones.total or self.procedimientos.total or self.media.total)


def _cambios(actuales: dict[str, object], nuevos: dict[str, object]) -> Cambios:
    return Cambios(
        crear=sorted(set(nuevos) - set(actuales)),
        actualizar=sorted(k for k in set(nuevos) & set(actuales) if nuevos[k] != actuales[k]),
        borrar=sorted(set(actuales) - set(nuevos)),
    )


def _filas(db: Session, modelo: type, proyecto_id: int) -> dict[str, object]:
    return {f.id: f for f in db.scalars(select(modelo).where(modelo.proyecto_id == proyecto_id))}


def planear(db: Session, proyecto_id: int, paquete: Paquete) -> Plan:
    secciones = _filas(db, ContenidoSeccion, proyecto_id)
    procedimientos = _filas(db, ContenidoProcedimiento, proyecto_id)
    medias_actuales = select(ContenidoMedia).where(ContenidoMedia.proyecto_id == proyecto_id)
    media = {m.procedimiento_id: m.huella for m in db.scalars(medias_actuales)}
    nuevos_proc = {d["id"]: (i, d) for i, d in enumerate(paquete.procedimientos)}
    return Plan(
        secciones=_cambios(
            {k: f.datos for k, f in secciones.items()}, {d["id"]: d for d in paquete.secciones}
        ),
        procedimientos=_cambios(
            {k: (f.orden, f.datos) for k, f in procedimientos.items()}, nuevos_proc
        ),
        media=_cambios(media, {k: a.huella for k, a in paquete.media.items()}),
        bloqueos=referencias.bloqueos(
            db, proyecto_id, [f.datos for f in secciones.values()], paquete.secciones
        ),
    )


@dataclass(frozen=True)
class Destino:
    proyecto_id: int
    modelo: type
    tipo: str


def _aplicar_documentos(
    db: Session, destino: Destino, cambios: Cambios, nuevos: dict[str, tuple], autor: str
) -> None:
    proyecto_id, modelo, tipo = destino.proyecto_id, destino.modelo, destino.tipo
    for clave in cambios.borrar:
        fila = db.get(modelo, {"proyecto_id": proyecto_id, "id": clave})
        versiones.registrar(db, proyecto_id, tipo, clave, "borrar", fila.datos, autor)
        db.delete(fila)
    for clave in cambios.crear + cambios.actualizar:
        orden, datos = nuevos[clave]
        fila = db.get(modelo, {"proyecto_id": proyecto_id, "id": clave})
        anterior = fila.datos if fila else None
        versiones.registrar(db, proyecto_id, tipo, clave, "importar", anterior, autor)
        if fila is None:
            fila = modelo(proyecto_id=proyecto_id, id=clave)
            db.add(fila)
        fila.orden = orden
        fila.datos = datos
        fila.actualizado = utcnow()
        fila.autor_email = autor


def aplicar(db: Session, proyecto_id: int, paquete: Paquete, plan: Plan, autor: str) -> None:
    secciones = {d["id"]: (d.get("orden") or 0, d) for d in paquete.secciones}
    procedimientos = {d["id"]: (i, d) for i, d in enumerate(paquete.procedimientos)}
    _aplicar_documentos(
        db, Destino(proyecto_id, ContenidoSeccion, "seccion"), plan.secciones, secciones, autor
    )
    _aplicar_documentos(
        db,
        Destino(proyecto_id, ContenidoProcedimiento, "procedimiento"),
        plan.procedimientos,
        procedimientos,
        autor,
    )
    for clave in plan.media.borrar:
        medias.borrar(db, proyecto_id, clave, autor)
    for clave in plan.media.crear + plan.media.actualizar:
        medias.guardar(db, proyecto_id, clave, paquete.media[clave], autor)
    db.commit()


def _nunca_editado(db: Session, proyecto_id: int) -> bool:
    return all(
        db.scalar(select(modelo).where(modelo.proyecto_id == proyecto_id).limit(1)) is None
        for modelo in (ContenidoSeccion, ContenidoProcedimiento, ContenidoMedia, ContenidoVersion)
    )


def importar_inicial(motor: Engine) -> bool:
    raiz = Path(settings.contenido_dir)
    Path(settings.media_dir).mkdir(parents=True, exist_ok=True)
    with Session(motor) as db:
        proyecto_id = proyectos.por_omision(db).id
        if not _nunca_editado(db, proyecto_id):
            return False
        paquete = de_directorio(raiz) if raiz.is_dir() else Paquete()
        if paquete.vacio:
            return False
        for error in paquete.errores:
            logger.warning("importación inicial: %s", error)
        try:
            aplicar(db, proyecto_id, paquete, planear(db, proyecto_id, paquete), AUTOR_INICIAL)
        except IntegrityError:
            db.rollback()
            return False
    logger.info(
        "importación inicial: %d secciones, %d procedimientos y %d animaciones desde %s",
        len(paquete.secciones),
        len(paquete.procedimientos),
        len(paquete.media),
        raiz,
    )
    return True
