from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.permisos import (
    ADMINISTRAR,
    APROBAR,
    EDITAR_CONTENIDO,
    GESTIONAR_FALLAS,
    VER_TABLERO,
)
from app.models.acceso import Acceso
from app.schemas.acceso import AccesoItem

PAGINAS_OTORGABLES = ("tablero", "fallas", "herramientas", "tecnico")
PERMISO_DE_PAGINA = {
    "tablero": (VER_TABLERO, APROBAR),
    "fallas": (GESTIONAR_FALLAS, APROBAR),
    "herramientas": (GESTIONAR_FALLAS, APROBAR),
    "aprobaciones": (APROBAR, GESTIONAR_FALLAS),
    "rondas": (GESTIONAR_FALLAS,),
    "tecnico": (GESTIONAR_FALLAS,),
    "admin": (ADMINISTRAR,),
    "editor": (EDITAR_CONTENIDO,),
}


def otorgadas(db: Session, email: str) -> frozenset[str]:
    acceso = db.scalar(select(Acceso).where(Acceso.usuario_email == email))
    paginas = acceso.paginas if acceso else []
    return frozenset(p for p in paginas if p in PAGINAS_OTORGABLES)


def efectivas(permisos: frozenset[str], concedidas: frozenset[str]) -> list[str]:
    return [
        pagina
        for pagina, requeridos in PERMISO_DE_PAGINA.items()
        if permisos.intersection(requeridos) or pagina in concedidas
    ]


def listar(db: Session) -> list[Acceso]:
    return list(db.scalars(select(Acceso).order_by(Acceso.usuario_email)))


def reemplazar(db: Session, items: list[AccesoItem]) -> list[Acceso]:
    db.execute(delete(Acceso))
    unicos = {i.usuario_email.strip().lower(): sorted(set(i.paginas)) for i in items}
    nuevos = [Acceso(usuario_email=e, paginas=p) for e, p in sorted(unicos.items()) if p]
    db.add_all(nuevos)
    db.commit()
    return nuevos
