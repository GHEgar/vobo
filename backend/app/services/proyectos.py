from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.contenido import ContenidoSeccion
from app.models.proyecto import CLAVE_POR_OMISION, NOMBRE_POR_OMISION, Proyecto
from app.models.ronda import Ronda

SOLO_ARCHIVOS = (
    "Con el contenido en archivos hay un solo proyecto; "
    "para varios proyectos usa CONTENIDO_FUENTE=base"
)


def _no_encontrado() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado")


def _conflicto(detalle: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detalle)


def asegurar_por_omision(db: Session) -> Proyecto:
    marcado = db.scalar(select(Proyecto).where(Proyecto.por_omision.is_(True)).limit(1))
    if marcado is not None:
        return marcado
    primero = db.scalar(select(Proyecto).order_by(Proyecto.orden, Proyecto.id).limit(1))
    if primero is None:
        primero = Proyecto(clave=CLAVE_POR_OMISION, nombre=NOMBRE_POR_OMISION, descripcion="")
        db.add(primero)
    primero.por_omision = True
    db.commit()
    db.refresh(primero)
    return primero


def por_omision(db: Session) -> Proyecto:
    marcado = db.scalar(select(Proyecto).where(Proyecto.por_omision.is_(True)).limit(1))
    return marcado if marcado is not None else asegurar_por_omision(db)


def de_clave(db: Session, clave: str) -> Proyecto:
    proyecto = db.scalar(select(Proyecto).where(Proyecto.clave == clave))
    if proyecto is None:
        raise _no_encontrado()
    return proyecto


def obtener_o_404(db: Session, proyecto_id: int) -> Proyecto:
    proyecto = db.get(Proyecto, proyecto_id)
    if proyecto is None:
        raise _no_encontrado()
    return proyecto


def de_ronda(db: Session, ronda_id: int) -> Proyecto:
    ronda = db.get(Ronda, ronda_id)
    if ronda is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ronda no encontrada")
    return obtener_o_404(db, ronda.proyecto_id)


def resolver(db: Session, ronda_id: int | None, clave: str | None) -> Proyecto:
    ronda = db.get(Ronda, ronda_id) if ronda_id is not None else None
    if ronda is not None:
        return obtener_o_404(db, ronda.proyecto_id)
    if clave:
        return de_clave(db, clave)
    return por_omision(db)


def ordenados(db: Session, con_archivados: bool = False) -> list[Proyecto]:
    consulta = select(Proyecto).order_by(Proyecto.orden, Proyecto.id)
    if not con_archivados:
        consulta = consulta.where(Proyecto.archivado.is_(False))
    return list(db.scalars(consulta))


def conteos(db: Session) -> tuple[dict[int, int], dict[int, int]]:
    rondas = db.execute(select(Ronda.proyecto_id, func.count()).group_by(Ronda.proyecto_id))
    secciones = db.execute(
        select(ContenidoSeccion.proyecto_id, func.count()).group_by(ContenidoSeccion.proyecto_id)
    )
    return dict(rondas.tuples().all()), dict(secciones.tuples().all())


def multiples() -> bool:
    return settings.contenido_en_base


def carpeta_media(proyecto_id: int, db: Session) -> str:
    proyecto = obtener_o_404(db, proyecto_id)
    return "" if proyecto.clave == CLAVE_POR_OMISION else f"{proyecto.clave}/"
