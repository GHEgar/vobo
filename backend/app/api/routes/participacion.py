from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import Actor, lectura_o_permiso
from app.core.database import get_db
from app.core.permisos import GESTIONAR_FALLAS
from app.schemas.participacion import Participacion
from app.services import participacion

router = APIRouter(prefix="/api/participacion", tags=["participacion"])


@router.get("", response_model=Participacion, response_model_exclude_none=True)
def obtener(
    proyectos: str = Query(default="", max_length=2000),
    ronda: int | None = Query(default=None),
    db: Session = Depends(get_db),
    _actor: Actor = Depends(lectura_o_permiso(GESTIONAR_FALLAS, "fallas")),
) -> Participacion:
    claves = [c.strip() for c in proyectos.split(",") if c.strip()]
    return participacion.calcular(db, claves, ronda)
