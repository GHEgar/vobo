from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import Actor, get_actor, proyecto_actual
from app.core.database import get_db
from app.models.proyecto import Proyecto
from app.schemas.busqueda import ResultadoBusqueda
from app.services import buscador, contenido, rondas, visibilidad

router = APIRouter(prefix="/api", tags=["buscar"])


@router.get("/buscar", response_model=list[ResultadoBusqueda])
def buscar(
    q: str = Query(default="", max_length=200),
    ronda: int | None = Query(default=None),
    db: Session = Depends(get_db),
    proyecto: Proyecto = Depends(proyecto_actual),
    actor: Actor = Depends(get_actor),
) -> list[ResultadoBusqueda]:
    palabras = buscador.palabras_de(q)
    if not palabras:
        return []
    actual = contenido.obtener(proyecto)
    asignadas: set[str] = set()
    if ronda is not None:
        rondas.obtener_o_404(db, ronda)
        asignadas = set(rondas.secciones_asignadas(db, ronda, actor.email))
    visibles = visibilidad.secciones_visibles(
        actual, asignadas, actor.ve(visibilidad.PAGINA_TECNICO)
    )
    return buscador.buscar(actual, visibles, palabras)
