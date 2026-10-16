from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import EMAIL_TOKEN_LECTURA, Actor, get_actor, proyecto_actual
from app.core.database import get_db
from app.core.permisos import GESTIONAR_FALLAS, VER_TABLERO
from app.models.proyecto import Proyecto
from app.schemas.presencia import PresenciaCreate, PresenciaResponse
from app.services import contenido, presencia, proyectos

router = APIRouter(prefix="/api/presencia", tags=["presencia"])


def _proyecto_de(db: Session, datos: PresenciaCreate) -> int | None:
    try:
        return proyectos.resolver(db, datos.ronda_id, datos.proyecto).id
    except HTTPException:
        return None


@router.post("", status_code=status.HTTP_204_NO_CONTENT)
def registrar_presencia(
    datos: PresenciaCreate,
    db: Session = Depends(get_db),
    actor: Actor = Depends(get_actor),
) -> Response:
    if actor.email != EMAIL_TOKEN_LECTURA:
        presencia.registrar(db, actor.email, actor.nombre, datos, _proyecto_de(db, datos))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("", response_model=list[PresenciaResponse])
def listar_presencia(
    db: Session = Depends(get_db),
    proyecto: Proyecto = Depends(proyecto_actual),
    actor: Actor = Depends(get_actor),
) -> list[PresenciaResponse]:
    if not (actor.puede(VER_TABLERO) or actor.puede(GESTIONAR_FALLAS)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Requiere permiso: {VER_TABLERO} o {GESTIONAR_FALLAS}",
        )
    return presencia.listar(db, contenido.obtener(proyecto), actor.email, proyecto.id)
