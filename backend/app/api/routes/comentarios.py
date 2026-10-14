from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import Actor, get_actor, lectura_o_permiso
from app.core.database import get_db
from app.core.permisos import GESTIONAR_FALLAS
from app.schemas.resultado import ComentarioResponse
from app.services import comentarios, contenido

router = APIRouter(prefix="/api/comentarios", tags=["comentarios"])


@router.get("", response_model=list[ComentarioResponse])
def listar_comentarios(
    ronda: int | None = Query(default=None),
    db: Session = Depends(get_db),
    _actor: Actor = Depends(lectura_o_permiso(GESTIONAR_FALLAS, "fallas")),
) -> list[ComentarioResponse]:
    return comentarios.listar(db, contenido.obtener(), ronda)


@router.get("/caso/{caso_id}", response_model=list[ComentarioResponse])
def comentarios_del_caso(
    caso_id: str,
    ronda: int = Query(...),
    db: Session = Depends(get_db),
    actor: Actor = Depends(get_actor),
) -> list[ComentarioResponse]:
    actual = contenido.obtener()
    contenido.caso_o_404(actual, caso_id)
    propio = None if actor.puede(GESTIONAR_FALLAS) else actor.email
    return comentarios.listar(db, actual, ronda, caso_id=caso_id, email=propio)
