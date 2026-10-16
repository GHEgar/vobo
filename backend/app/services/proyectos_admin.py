from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.contenido import ContenidoMedia
from app.models.proyecto import Proyecto
from app.schemas.proyecto import ProyectoAdmin, ProyectoCambios, ProyectoCrear, ProyectosAdmin
from app.services import contenido_media as medias
from app.services import proyectos


def _conflicto(detalle: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detalle)


def estado(db: Session) -> ProyectosAdmin:
    proyectos.asegurar_por_omision(db)
    rondas, secciones = proyectos.conteos(db)
    return ProyectosAdmin(
        fuente=settings.contenido_fuente,
        multiples=proyectos.multiples(),
        motivo="" if proyectos.multiples() else proyectos.SOLO_ARCHIVOS,
        proyectos=[
            ProyectoAdmin.model_validate(p, from_attributes=True).model_copy(
                update={"rondas": rondas.get(p.id, 0), "secciones": secciones.get(p.id, 0)}
            )
            for p in proyectos.ordenados(db, con_archivados=True)
        ],
    )


def crear(db: Session, datos: ProyectoCrear) -> Proyecto:
    if not proyectos.multiples():
        raise _conflicto(proyectos.SOLO_ARCHIVOS)
    if db.scalar(select(Proyecto).where(Proyecto.clave == datos.clave)) is not None:
        raise _conflicto("Ya existe un proyecto con esa clave")
    orden = (db.scalar(select(func.max(Proyecto.orden))) or 0) + 10
    proyecto = Proyecto(
        clave=datos.clave,
        nombre=datos.nombre,
        descripcion=datos.descripcion.strip(),
        color_nombre=datos.color_nombre,
        orden=orden,
    )
    db.add(proyecto)
    db.commit()
    db.refresh(proyecto)
    return proyecto


def _marcar_por_omision(db: Session, proyecto: Proyecto) -> None:
    if proyecto.archivado:
        raise _conflicto("Un proyecto archivado no puede ser el por omisión")
    db.execute(update(Proyecto).where(Proyecto.id != proyecto.id).values(por_omision=False))
    proyecto.por_omision = True


def actualizar(db: Session, proyecto: Proyecto, cambios: ProyectoCambios) -> Proyecto:
    campos = cambios.model_fields_set
    if cambios.nombre is not None:
        proyecto.nombre = cambios.nombre
    if cambios.descripcion is not None:
        proyecto.descripcion = cambios.descripcion.strip()
    if "color_nombre" in campos:
        proyecto.color_nombre = cambios.color_nombre
    if cambios.por_omision is False and proyecto.por_omision:
        raise _conflicto("Marca otro proyecto por omisión; siempre debe haber uno")
    if cambios.archivado is not None:
        if cambios.archivado and (proyecto.por_omision or cambios.por_omision):
            raise _conflicto("Marca otro proyecto por omisión antes de archivar este")
        proyecto.archivado = cambios.archivado
    if cambios.por_omision:
        _marcar_por_omision(db, proyecto)
    db.commit()
    db.refresh(proyecto)
    return proyecto


def ordenar(db: Session, ids: list[int]) -> None:
    todos = {p.id: p for p in proyectos.ordenados(db, con_archivados=True)}
    if sorted(ids) != sorted(todos):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="El orden debe incluir todos los proyectos una sola vez",
        )
    for posicion, proyecto_id in enumerate(ids, start=1):
        todos[proyecto_id].orden = posicion * 10
    db.commit()


def borrar(db: Session, proyecto: Proyecto) -> None:
    if proyecto.por_omision:
        raise _conflicto("No se puede borrar el proyecto por omisión")
    rondas, _ = proyectos.conteos(db)
    if rondas.get(proyecto.id):
        raise _conflicto("El proyecto tiene rondas; archívalo en vez de borrarlo")
    archivos = list(
        db.scalars(select(ContenidoMedia.archivo).where(ContenidoMedia.proyecto_id == proyecto.id))
    )
    db.delete(proyecto)
    db.commit()
    medias.quitar_archivos(archivos)
