from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import EMAIL_TOKEN_LECTURA, Actor, get_actor, require_permission
from app.core.database import get_db
from app.core.permisos import GESTIONAR_FALLAS
from app.models.aviso import Aviso
from app.models.usuario import Usuario
from app.schemas.aviso import AvisoCreate, AvisoResponse, NoLeidosResponse, PersonaAviso
from app.services import avisos

router = APIRouter(prefix="/api/avisos", tags=["avisos"])


@router.get("", response_model=list[AvisoResponse])
def mis_avisos(db: Session = Depends(get_db), actor: Actor = Depends(get_actor)) -> list[Aviso]:
    return avisos.listar(db, actor.email)


@router.get("/no-leidos", response_model=NoLeidosResponse)
def no_leidos(db: Session = Depends(get_db), actor: Actor = Depends(get_actor)) -> NoLeidosResponse:
    return NoLeidosResponse(total=avisos.no_leidos(db, actor.email))


@router.get("/personas", response_model=list[PersonaAviso])
def personas(
    db: Session = Depends(get_db),
    _actor: Actor = Depends(require_permission(GESTIONAR_FALLAS)),
) -> list[Usuario]:
    return avisos.personas(db, EMAIL_TOKEN_LECTURA)


@router.post("/leidos", response_model=NoLeidosResponse)
def marcar_todos(
    db: Session = Depends(get_db), actor: Actor = Depends(get_actor)
) -> NoLeidosResponse:
    avisos.marcar_todos(db, actor.email)
    return NoLeidosResponse(total=0)


@router.post("/{aviso_id}/leido", response_model=AvisoResponse)
def marcar_leido(
    aviso_id: int, db: Session = Depends(get_db), actor: Actor = Depends(get_actor)
) -> Aviso:
    return avisos.marcar(db, actor.email, aviso_id)


@router.post("", response_model=list[AvisoResponse], status_code=status.HTTP_201_CREATED)
def crear_aviso(
    datos: AvisoCreate,
    db: Session = Depends(get_db),
    actor: Actor = Depends(require_permission(GESTIONAR_FALLAS)),
) -> list[Aviso]:
    return avisos.crear(db, datos, actor.email, actor.nombre)
