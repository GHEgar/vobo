from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import Actor, lectura_o_permiso, require_permission
from app.core.database import get_db
from app.core.permisos import APROBAR
from app.schemas.aprobacion import AprobacionCreate, AprobacionesResponse
from app.services import aprobaciones, contenido, proyectos

router = APIRouter(prefix="/api/aprobaciones", tags=["aprobaciones"])


@router.get("", response_model=AprobacionesResponse)
def listar_aprobaciones(
    ronda: int = Query(...),
    db: Session = Depends(get_db),
    _actor: Actor = Depends(lectura_o_permiso(APROBAR, "aprobaciones")),
) -> AprobacionesResponse:
    return aprobaciones.estado(db, contenido.obtener(proyectos.de_ronda(db, ronda)), ronda)


@router.post("", response_model=AprobacionesResponse, status_code=status.HTTP_201_CREATED)
def registrar_aprobaciones(
    datos: AprobacionCreate,
    db: Session = Depends(get_db),
    actor: Actor = Depends(require_permission(APROBAR)),
) -> AprobacionesResponse:
    actual = contenido.obtener(proyectos.de_ronda(db, datos.ronda_id))
    aprobaciones.registrar(db, actual, actor.email, actor.nombre, datos)
    return aprobaciones.estado(db, actual, datos.ronda_id)
