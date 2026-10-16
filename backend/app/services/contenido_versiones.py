from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.contenido import ContenidoVersion

TIPOS = ("seccion", "procedimiento", "media")


def registrar(
    db: Session,
    proyecto_id: int,
    tipo: str,
    objeto_id: str,
    accion: str,
    datos: dict | None,
    autor: str,
) -> ContenidoVersion:
    version = ContenidoVersion(
        proyecto_id=proyecto_id,
        tipo=tipo,
        objeto_id=objeto_id,
        accion=accion,
        datos=datos,
        autor_email=autor,
    )
    db.add(version)
    return version


def de(db: Session, proyecto_id: int, tipo: str, objeto_id: str) -> list[ContenidoVersion]:
    return list(
        db.scalars(
            select(ContenidoVersion)
            .where(
                ContenidoVersion.proyecto_id == proyecto_id,
                ContenidoVersion.tipo == tipo,
                ContenidoVersion.objeto_id == objeto_id,
            )
            .order_by(ContenidoVersion.id.desc())
        )
    )


def ultima(db: Session, proyecto_id: int | None = None) -> int:
    consulta = select(func.max(ContenidoVersion.id))
    if proyecto_id is not None:
        consulta = consulta.where(ContenidoVersion.proyecto_id == proyecto_id)
    return db.scalar(consulta) or 0
