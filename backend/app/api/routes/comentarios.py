from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import (
    Actor,
    get_actor,
    lectura_o_permiso,
    proyecto_actual,
    require_permission,
)
from app.core.database import get_db
from app.core.permisos import GESTIONAR_FALLAS
from app.models.proyecto import Proyecto
from app.schemas.resultado import ComentarioResponse
from app.schemas.seguimiento import ComentarioUpdate, EventoSeguimiento, RespuestaCreate
from app.services import comentarios, comentarios_seguimiento, contenido, proyectos, seguimiento

router = APIRouter(prefix="/api/comentarios", tags=["comentarios"])


@router.get("", response_model=list[ComentarioResponse])
def listar_comentarios(
    ronda: int | None = Query(default=None),
    db: Session = Depends(get_db),
    proyecto: Proyecto = Depends(proyecto_actual),
    _actor: Actor = Depends(lectura_o_permiso(GESTIONAR_FALLAS, "fallas")),
) -> list[ComentarioResponse]:
    return comentarios.listar(db, contenido.obtener(proyecto), ronda, proyecto_id=proyecto.id)


@router.get("/caso/{caso_id}", response_model=list[ComentarioResponse])
def comentarios_del_caso(
    caso_id: str,
    ronda: int = Query(...),
    db: Session = Depends(get_db),
    actor: Actor = Depends(get_actor),
) -> list[ComentarioResponse]:
    actual = contenido.obtener(proyectos.de_ronda(db, ronda))
    contenido.caso_o_404(actual, caso_id)
    propio = None if actor.puede(GESTIONAR_FALLAS) else actor.email
    return comentarios.listar(db, actual, ronda, caso_id=caso_id, email=propio)


def _visible(db: Session, comentario_id: int) -> ComentarioResponse:
    fila = comentarios_seguimiento.obtener_o_404(db, comentario_id)
    actual = contenido.obtener(proyectos.de_ronda(db, fila.ronda_id))
    listados = comentarios.listar(
        db, actual, fila.ronda_id, caso_id=fila.caso_id, email=fila.usuario_email
    )
    encontrado = next((c for c in listados if c.id == fila.id), None)
    if encontrado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="El comentario ya no existe"
        )
    return encontrado


@router.patch("/{comentario_id}", response_model=ComentarioResponse)
def actualizar_comentario(
    comentario_id: int,
    cambios: ComentarioUpdate,
    db: Session = Depends(get_db),
    actor: Actor = Depends(require_permission(GESTIONAR_FALLAS)),
) -> ComentarioResponse:
    _visible(db, comentario_id)
    comentarios_seguimiento.actualizar(db, comentario_id, cambios, actor.email)
    return _visible(db, comentario_id)


@router.post(
    "/{comentario_id}/respuestas",
    response_model=EventoSeguimiento,
    status_code=status.HTTP_201_CREATED,
)
def responder_comentario(
    comentario_id: int,
    datos: RespuestaCreate,
    db: Session = Depends(get_db),
    actor: Actor = Depends(require_permission(GESTIONAR_FALLAS)),
) -> EventoSeguimiento:
    _visible(db, comentario_id)
    fila = comentarios_seguimiento.obtener_o_404(db, comentario_id)
    return seguimiento.responder(db, "comentario", fila, actor.email, datos.texto)
