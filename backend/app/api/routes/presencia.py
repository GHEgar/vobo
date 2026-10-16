from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import (
    EMAIL_TOKEN_LECTURA,
    SEGUIMIENTO,
    Actor,
    get_actor,
    proyecto_actual,
)
from app.core.database import get_db
from app.models.proyecto import Proyecto
from app.schemas.presencia import PresenciaCreate, PresenciaResponse
from app.services import agente, contenido, presencia, proyectos

router = APIRouter(prefix="/api/presencia", tags=["presencia"])


def _proyecto_de(db: Session, datos: PresenciaCreate) -> int | None:
    try:
        return proyectos.resolver(db, datos.ronda_id, datos.proyecto).id
    except HTTPException:
        return None


@router.post("", status_code=status.HTTP_204_NO_CONTENT)
def registrar_presencia(
    datos: PresenciaCreate,
    request: Request,
    db: Session = Depends(get_db),
    actor: Actor = Depends(get_actor),
) -> Response:
    if actor.email != EMAIL_TOKEN_LECTURA:
        presencia.registrar(
            db,
            actor.email,
            actor.nombre,
            datos,
            _proyecto_de(db, datos),
            agente.describir(request.headers.get("user-agent")),
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("", response_model=list[PresenciaResponse])
def listar_presencia(
    db: Session = Depends(get_db),
    proyecto: Proyecto = Depends(proyecto_actual),
    actor: Actor = Depends(SEGUIMIENTO),
) -> list[PresenciaResponse]:
    return presencia.listar(db, contenido.obtener(proyecto), actor.email, proyecto.id)
