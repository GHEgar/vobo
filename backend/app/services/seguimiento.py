from collections import defaultdict
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.time import utcnow
from app.models.falla import Falla
from app.models.seguimiento import ComentarioSeguimiento, Seguimiento
from app.models.usuario import Usuario
from app.schemas.seguimiento import EventoSeguimiento


def nombres(db: Session) -> dict[str, str]:
    return {u.email: u.nombre for u in db.scalars(select(Usuario))}


def registrar(
    db: Session,
    objeto: str,
    objeto_id: int,
    autor: str,
    accion: str,
    texto: str = "",
    anterior: str | None = None,
    nuevo: str | None = None,
) -> Seguimiento:
    evento = Seguimiento(
        objeto=objeto,
        objeto_id=objeto_id,
        autor_email=autor,
        accion=accion,
        texto=texto,
        anterior=anterior,
        nuevo=nuevo,
        creado=utcnow(),
    )
    db.add(evento)
    return evento


def serializar(evento: Seguimiento, conocidos: dict[str, str]) -> EventoSeguimiento:
    return EventoSeguimiento(
        id=evento.id,
        accion=evento.accion,
        autor_email=evento.autor_email,
        autor=conocidos.get(evento.autor_email, evento.autor_email),
        texto=evento.texto or "",
        anterior=evento.anterior,
        nuevo=evento.nuevo,
        creado=evento.creado,
    )


def de_objetos(
    db: Session, objeto: str, ids: list[int], conocidos: dict[str, str]
) -> dict[int, list[EventoSeguimiento]]:
    if not ids:
        return {}
    consulta = (
        select(Seguimiento)
        .where(Seguimiento.objeto == objeto, Seguimiento.objeto_id.in_(ids))
        .order_by(Seguimiento.creado, Seguimiento.id)
    )
    agrupados: dict[int, list[EventoSeguimiento]] = defaultdict(list)
    for evento in db.scalars(consulta):
        agrupados[evento.objeto_id].append(serializar(evento, conocidos))
    return agrupados


def cambiar_estado(
    db: Session,
    objeto: str,
    registro: Falla | ComentarioSeguimiento,
    nuevo: str,
    actor: str,
    final: str,
    campos: tuple[str, str],
) -> None:
    anterior = registro.estado
    if nuevo == anterior:
        return
    registro.estado = nuevo
    en, por = campos
    if nuevo == final:
        setattr(registro, en, utcnow())
        setattr(registro, por, actor)
    elif anterior == final:
        setattr(registro, en, None)
        setattr(registro, por, None)
    registrar(db, objeto, registro.id, actor, "estado", anterior=anterior, nuevo=nuevo)


def cambiar_plazo(
    db: Session,
    objeto: str,
    registro: Falla | ComentarioSeguimiento,
    plazo: date | None,
    actor: str,
) -> None:
    anterior = registro.plazo
    if plazo == anterior:
        return
    registro.plazo = plazo
    registro.plazo_por = actor if plazo is not None else None
    registrar(
        db,
        objeto,
        registro.id,
        actor,
        "plazo",
        anterior=anterior.isoformat() if anterior else None,
        nuevo=plazo.isoformat() if plazo else None,
    )


def responder(
    db: Session, objeto: str, objeto_id: int, autor: str, texto: str
) -> EventoSeguimiento:
    evento = registrar(db, objeto, objeto_id, autor, "respuesta", texto=texto)
    db.commit()
    db.refresh(evento)
    return serializar(evento, nombres(db))
