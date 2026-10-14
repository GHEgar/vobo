from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.ronda import Asignacion, Ronda
from app.schemas.ronda import AsignacionItem
from app.services import evidencias


def obtener_o_404(db: Session, ronda_id: int) -> Ronda:
    ronda = db.get(Ronda, ronda_id)
    if ronda is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ronda no encontrada")
    return ronda


def abierta_o_409(db: Session, ronda_id: int) -> Ronda:
    ronda = obtener_o_404(db, ronda_id)
    if not ronda.abierta:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La ronda está cerrada; ya no admite cambios",
        )
    return ronda


def borrar(db: Session, ronda: Ronda) -> None:
    rutas = [e.ruta for falla in ronda.fallas for e in falla.evidencias]
    db.delete(ronda)
    db.commit()
    for relativa in rutas:
        try:
            evidencias.ruta_absoluta(relativa).unlink(missing_ok=True)
        except HTTPException:
            continue


def secciones_asignadas(db: Session, ronda_id: int, email: str) -> list[str]:
    consulta = select(Asignacion.seccion_id).where(
        Asignacion.ronda_id == ronda_id, Asignacion.usuario_email == email
    )
    return sorted(db.scalars(consulta).all())


def reemplazar_asignaciones(
    db: Session, ronda: Ronda, items: list[AsignacionItem], secciones_validas: set[str]
) -> list[Asignacion]:
    db.execute(delete(Asignacion).where(Asignacion.ronda_id == ronda.id))
    unicas = {
        (i.usuario_email.strip().lower(), i.seccion_id)
        for i in items
        if i.seccion_id in secciones_validas
    }
    nuevas = [
        Asignacion(ronda_id=ronda.id, usuario_email=email, seccion_id=seccion)
        for email, seccion in sorted(unicas)
    ]
    db.add_all(nuevas)
    db.commit()
    return nuevas
