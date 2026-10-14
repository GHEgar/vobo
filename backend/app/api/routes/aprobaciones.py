from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import Actor, lectura_o_permiso, require_permission
from app.core.database import get_db
from app.core.permisos import APROBAR
from app.schemas.aprobacion import AprobacionCreate, AprobacionesResponse
from app.services import aprobaciones, contenido, rondas

router = APIRouter(prefix="/api/aprobaciones", tags=["aprobaciones"])


@router.get("", response_model=AprobacionesResponse)
def listar_aprobaciones(
    ronda: int = Query(...),
    db: Session = Depends(get_db),
    _actor: Actor = Depends(lectura_o_permiso(APROBAR, "aprobaciones")),
) -> AprobacionesResponse:
    rondas.obtener_o_404(db, ronda)
    return aprobaciones.estado(db, contenido.obtener(), ronda)


@router.post("", response_model=AprobacionesResponse, status_code=status.HTTP_201_CREATED)
def registrar_aprobaciones(
    datos: AprobacionCreate,
    db: Session = Depends(get_db),
    actor: Actor = Depends(require_permission(APROBAR)),
) -> AprobacionesResponse:
    rondas.obtener_o_404(db, datos.ronda_id)
    actual = contenido.obtener()
    aprobaciones.registrar(db, actual, actor.email, actor.nombre, datos)
    return aprobaciones.estado(db, actual, datos.ronda_id)
