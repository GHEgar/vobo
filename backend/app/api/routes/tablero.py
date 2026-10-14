from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import Actor, lectura_o_permiso
from app.core.database import get_db
from app.core.permisos import VER_TABLERO
from app.schemas.tablero import TableroResponse
from app.services import contenido, rondas, tablero

router = APIRouter(prefix="/api/tablero", tags=["tablero"])


@router.get("", response_model=TableroResponse)
def obtener_tablero(
    ronda: int = Query(...),
    audiencia: Literal["todas", "funcional", "tecnica"] = Query(default="todas"),
    db: Session = Depends(get_db),
    _actor: Actor = Depends(lectura_o_permiso(VER_TABLERO, "tablero")),
) -> TableroResponse:
    return tablero.calcular(db, contenido.obtener(), rondas.obtener_o_404(db, ronda), audiencia)
