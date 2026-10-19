from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.aviso import Aviso
from app.models.falla import Falla
from app.models.ronda import Ronda
from app.models.seguimiento import ComentarioSeguimiento
from app.models.usuario import Usuario

Registro = Falla | ComentarioSeguimiento

MESES = (
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
)

TITULOS_RESPUESTA = {
    "falla": "Respuesta a tu reporte de {caso}",
    "comentario": "Respuesta a tu comentario en {caso}",
}

PLANTILLAS_ESTADO = {
    "falla": {
        "en_curso": (
            "Estamos trabajando en tu reporte de {caso}",
            "Estamos trabajando en tu reporte de {caso}.",
        ),
        "lista_para_revalidar": (
            "Ya puedes volver a probar {caso}",
            "Ya puedes volver a probar {caso}.",
        ),
        "cerrada": (
            "Tu reporte de {caso} fue atendido",
            "Tu reporte de {caso} ya fue atendido.",
        ),
    },
    "comentario": {
        "en_curso": (
            "Estamos trabajando en tu comentario en {caso}",
            "Estamos trabajando en tu comentario en {caso}.",
        ),
        "resuelto": (
            "Tu comentario en {caso} fue atendido",
            "Tu comentario en {caso} ya fue atendido.",
        ),
    },
}


def fecha_legible(dia: date) -> str:
    return f"{dia.day} de {MESES[dia.month - 1]} de {dia.year}"


def _con_plazo(partes: list[str], fila: Registro) -> str:
    if fila.plazo is not None:
        partes.append(f"Plazo: {fecha_legible(fila.plazo)}")
    return "\n\n".join(p for p in partes if p)


def _nombre(db: Session, email: str) -> str:
    return db.scalar(select(Usuario.nombre).where(Usuario.email == email)) or ""


def _crear(
    db: Session, objeto: str, fila: Registro, actor_email: str, titulo: str, mensaje: str
) -> Aviso | None:
    if fila.usuario_email == actor_email:
        return None
    ronda = db.get(Ronda, fila.ronda_id)
    aviso = Aviso(
        usuario_email=fila.usuario_email,
        titulo=titulo[:200],
        mensaje=mensaje,
        falla_id=fila.id if objeto == "falla" else None,
        caso_id=fila.caso_id,
        proyecto_id=ronda.proyecto_id if ronda is not None else None,
        autor_email=actor_email,
        autor_nombre=_nombre(db, actor_email),
    )
    db.add(aviso)
    return aviso


def avisar_respuesta(
    db: Session, objeto: str, fila: Registro, actor_email: str, texto: str
) -> Aviso | None:
    titulo = TITULOS_RESPUESTA[objeto].format(caso=fila.caso_id)
    return _crear(db, objeto, fila, actor_email, titulo, _con_plazo([texto.strip()], fila))


def avisar_estado(db: Session, objeto: str, fila: Registro, actor_email: str) -> Aviso | None:
    plantilla = PLANTILLAS_ESTADO[objeto].get(fila.estado)
    if plantilla is None:
        return None
    titulo, mensaje = (parte.format(caso=fila.caso_id) for parte in plantilla)
    partes = [mensaje]
    nota = (getattr(fila, "nota_resolucion", "") or "").strip()
    if objeto == "falla" and fila.estado == "cerrada" and nota:
        partes.append(f"Nota de resolución: {nota}")
    return _crear(db, objeto, fila, actor_email, titulo, _con_plazo(partes, fila))
