from datetime import datetime, timedelta

from sqlalchemy import case, func, or_, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session

from app.core.time import como_utc, utcnow
from app.models.presencia import Presencia
from app.schemas.presencia import PresenciaCreate, PresenciaResponse, ResumenPresencia
from app.services.agente import Agente
from app.services.contenido import Contenido

VENTANA = timedelta(minutes=10)
ACTIVO = timedelta(minutes=2)


def registrar(
    db: Session,
    email: str,
    nombre: str,
    datos: PresenciaCreate,
    proyecto_id: int | None,
    agente: Agente,
) -> None:
    ahora = utcnow()
    valores = {
        "nombre": nombre[:200],
        "ruta": datos.ruta,
        "caso_id": datos.caso_id,
        "paso": datos.paso,
        "seccion_id": datos.seccion_id,
        "accion": datos.accion,
        "ronda_id": datos.ronda_id,
        "proyecto_id": proyecto_id,
        "actualizado": ahora,
        "navegador": agente.navegador,
        "agente": agente.crudo,
        "dispositivo": agente.dispositivo,
        "pantalla": datos.pantalla,
    }
    reinicio = case(
        (Presencia.actualizado < ahora - VENTANA, ahora),
        else_=func.coalesce(Presencia.desde, ahora),
    )
    sentencia = insert(Presencia).values(usuario_email=email, desde=ahora, **valores)
    db.execute(
        sentencia.on_conflict_do_update(
            index_elements=["usuario_email"], set_={**valores, "desde": reinicio}
        )
    )
    db.commit()


def _segundos(ahora: datetime, momento: datetime | None) -> int:
    return max(0, int((ahora - (como_utc(momento) or ahora)).total_seconds()))


def _titulo_seccion(contenido: Contenido, seccion_id: str | None) -> str:
    if not seccion_id:
        return ""
    return next((s.titulo for s in contenido.respuesta.secciones if s.id == seccion_id), "")


def _serializar(
    fila: Presencia, contenido: Contenido, solicitante: str, ahora: datetime
) -> PresenciaResponse:
    ubicado = contenido.casos.get(fila.caso_id) if fila.caso_id else None
    seccion_id = fila.seccion_id or (ubicado.seccion_id if ubicado else None)
    segundos = _segundos(ahora, fila.actualizado)
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
        navegador=fila.navegador or "",
        dispositivo=fila.dispositivo or "escritorio",
        pantalla=fila.pantalla,
        desde=como_utc(fila.desde),
        sesion_segundos=_segundos(ahora, fila.desde) if fila.desde else 0,
    )


def listar(
    db: Session, contenido: Contenido, solicitante: str, proyecto_id: int
) -> list[PresenciaResponse]:
    ahora = utcnow()
    consulta = (
        select(Presencia)
        .where(
            Presencia.actualizado >= ahora - VENTANA,
            or_(Presencia.proyecto_id == proyecto_id, Presencia.proyecto_id.is_(None)),
        )
        .order_by(Presencia.actualizado.desc())
    )
    return [_serializar(f, contenido, solicitante, ahora) for f in db.scalars(consulta)]


def resumir(presentes: list[PresenciaResponse]) -> ResumenPresencia:
    activos = sum(1 for p in presentes if p.estado == "activo")
    return ResumenPresencia(activos=activos, inactivos=len(presentes) - activos)
