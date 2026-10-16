from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import Actor, lectura_o_sesion, require_permission
from app.core.database import get_db
from app.core.permisos import GESTIONAR_FALLAS
from app.models.decision import Decision
from app.schemas.herramienta import DecisionResponse, DecisionUpdate, HerramientaResumen
from app.services import contenido, herramientas, proyectos, rondas

router = APIRouter(prefix="/api", tags=["herramientas"])


@router.get("/herramientas", response_model=list[HerramientaResumen])
def listar_herramientas(
    ronda: int = Query(...),
    db: Session = Depends(get_db),
    _actor: Actor = Depends(lectura_o_sesion),
) -> list[HerramientaResumen]:
    actual = rondas.obtener_o_404(db, ronda)
    return herramientas.resumir(db, contenido.obtener(proyectos.de_ronda(db, ronda)), actual)


@router.put("/decisiones/{herramienta_id}", response_model=DecisionResponse)
def decidir(
    herramienta_id: str,
    datos: DecisionUpdate,
    db: Session = Depends(get_db),
    actor: Actor = Depends(require_permission(GESTIONAR_FALLAS)),
) -> Decision:
    actual = contenido.obtener(proyectos.de_ronda(db, datos.ronda_id))
    return herramientas.decidir(db, actual, herramienta_id, datos, actor.email)
