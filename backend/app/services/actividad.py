from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.time import como_utc
from app.models.proyecto import Proyecto
from app.models.usuario import Usuario
from app.schemas.actividad import EventoActividad, PaginaActividad
from app.services.actividad_eventos import FUENTES
from app.services.actividad_fuentes import Contexto
from app.services.contenido import Contenido

SEPARADOR = "|"


def cursor(evento: EventoActividad) -> str:
    return f"{evento.cuando.isoformat()}{SEPARADOR}{evento.id}"


def leer_cursor(valor: str | None) -> tuple[datetime | None, str]:
    if not valor:
        return None, ""
    momento, _, desempate = valor.partition(SEPARADOR)
    try:
        hasta = como_utc(datetime.fromisoformat(momento))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Cursor inválido"
        ) from None
    return hasta, desempate


def listar(
    db: Session,
    contenido: Contenido,
    proyecto: Proyecto,
    limite: int,
    tipos: list[str] | None = None,
    usuario: str | None = None,
    ronda: int | None = None,
    antes: str | None = None,
) -> PaginaActividad:
    hasta, desempate = leer_cursor(antes)
    ctx = Contexto(
        db=db,
        contenido=contenido,
        proyecto=proyecto,
        limite=limite,
        usuario=usuario,
        ronda=ronda,
        hasta=hasta,
        desempate=desempate,
        nombres={u.email: u.nombre for u in db.scalars(select(Usuario))},
    )
    elegidas = [FUENTES[t] for t in (tipos or FUENTES) if t in FUENTES]
    eventos = sorted(
        (e for fuente in elegidas for e in fuente(ctx) if ctx.admite(e)),
        key=lambda e: (e.cuando, e.id),
        reverse=True,
    )
    pagina = eventos[:limite]
    siguiente = cursor(pagina[-1]) if len(eventos) > limite else None
    return PaginaActividad(eventos=pagina, siguiente=siguiente)
