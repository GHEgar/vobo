from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.api.deps import Actor, get_actor
from app.core.database import get_db
from app.core.permisos import GESTIONAR_FALLAS
from app.schemas.cuenta import CuentaPrueba
from app.services import contenido, cuentas, rondas, visibilidad

router = APIRouter(prefix="/api/cuentas-prueba", tags=["cuentas"])


def _cuentas_de_sus_casos(db: Session, actor: Actor, ronda: int) -> list[str]:
    rondas.obtener_o_404(db, ronda)
    actual = contenido.obtener()
    asignadas = set(rondas.secciones_asignadas(db, ronda, actor.email))
    visibles = visibilidad.secciones_visibles(
        actual, asignadas, actor.ve(visibilidad.PAGINA_TECNICO)
    )
    return [
        (caso.cuenta or "").lower()
        for seccion in actual.respuesta.secciones
        if seccion.id in visibles
        for caso in seccion.casos
    ]


@router.get("", response_model=list[CuentaPrueba])
def listar_cuentas(
    response: Response,
    ronda: int | None = Query(default=None),
    db: Session = Depends(get_db),
    actor: Actor = Depends(get_actor),
) -> list[CuentaPrueba]:
    response.headers["Cache-Control"] = "no-store"
    todas = cuentas.listar()
    if ronda is None or actor.puede(GESTIONAR_FALLAS):
        return todas
    usadas = _cuentas_de_sus_casos(db, actor, ronda)
    return [c for c in todas if any(c.email.split("@", 1)[0].lower() in u for u in usadas)]
