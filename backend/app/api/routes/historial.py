from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import SEGUIMIENTO, Actor, proyecto_actual
from app.core.database import get_db
from app.models.proyecto import Proyecto
from app.schemas.historial import PuntoAvance
from app.services import contenido, historial, rondas

router = APIRouter(prefix="/api/historial", tags=["historial"])

DIAS_MAXIMOS = 731


@router.get("/avance", response_model=list[PuntoAvance])
def avance(
    ronda: int | None = Query(default=None),
    desde: date | None = Query(default=None),
    hasta: date | None = Query(default=None),
    db: Session = Depends(get_db),
    proyecto: Proyecto = Depends(proyecto_actual),
    _actor: Actor = Depends(SEGUIMIENTO),
) -> list[PuntoAvance]:
    if desde and hasta and (desde > hasta or (hasta - desde).days > DIAS_MAXIMOS):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"El rango debe ir de desde a hasta y no pasar de {DIAS_MAXIMOS} días",
        )
    if ronda is not None:
        rondas.obtener_o_404(db, ronda)
    casos = set(contenido.obtener(proyecto).casos)
    alcance = historial.rondas_en_alcance(db, proyecto.id, ronda)
    return historial.avance(db, alcance, casos, desde, hasta)
