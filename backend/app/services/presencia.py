from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session

from app.core.time import como_utc, utcnow
from app.models.presencia import Presencia
from app.schemas.presencia import PresenciaCreate, PresenciaResponse
from app.services.contenido import Contenido

VENTANA = timedelta(minutes=10)
ACTIVO = timedelta(minutes=2)


def registrar(db: Session, email: str, nombre: str, datos: PresenciaCreate) -> None:
    valores = {
        "nombre": nombre[:200],
        "ruta": datos.ruta,
        "caso_id": datos.caso_id,
        "paso": datos.paso,
        "seccion_id": datos.seccion_id,
        "accion": datos.accion,
        "ronda_id": datos.ronda_id,
        "actualizado": utcnow(),
    }
    sentencia = insert(Presencia).values(usuario_email=email, **valores)
    db.execute(sentencia.on_conflict_do_update(index_elements=["usuario_email"], set_=valores))
    db.commit()


def _titulo_seccion(contenido: Contenido, seccion_id: str | None) -> str:
    if not seccion_id:
        return ""
    return next((s.titulo for s in contenido.respuesta.secciones if s.id == seccion_id), "")


def _serializar(
    fila: Presencia, contenido: Contenido, solicitante: str, ahora: datetime
) -> PresenciaResponse:
    ubicado = contenido.casos.get(fila.caso_id) if fila.caso_id else None
    seccion_id = fila.seccion_id or (ubicado.seccion_id if ubicado else None)
    segundos = max(0, int((ahora - (como_utc(fila.actualizado) or ahora)).total_seconds()))
    return PresenciaResponse(
        email=fila.usuario_email,
        nombre=fila.nombre or fila.usuario_email,
        ruta=fila.ruta,
        caso_id=fila.caso_id,
        caso_titulo=ubicado.caso.titulo if ubicado else "",
        paso=fila.paso,
        pasos_total=len(ubicado.caso.pasos) if ubicado else None,
        seccion_id=seccion_id,
        seccion_titulo=_titulo_seccion(contenido, seccion_id),
        accion=fila.accion,
        ronda_id=fila.ronda_id,
        estado="activo" if segundos < ACTIVO.total_seconds() else "inactivo",
        hace_segundos=segundos,
        yo=fila.usuario_email == solicitante,
    )


def listar(db: Session, contenido: Contenido, solicitante: str) -> list[PresenciaResponse]:
    ahora = utcnow()
    consulta = (
        select(Presencia)
        .where(Presencia.actualizado >= ahora - VENTANA)
        .order_by(Presencia.actualizado.desc())
    )
    return [_serializar(f, contenido, solicitante, ahora) for f in db.scalars(consulta)]
