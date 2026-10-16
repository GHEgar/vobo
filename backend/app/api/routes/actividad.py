from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import SEGUIMIENTO, Actor, proyecto_actual
from app.core.database import get_db
from app.models.proyecto import Proyecto
from app.schemas.actividad import TIPOS_EVENTO, PaginaActividad
from app.schemas.presencia import ResumenPresencia
from app.services import actividad, contenido, presencia

router = APIRouter(prefix="/api/actividad", tags=["actividad"])


def _tipos(valor: str | None) -> list[str] | None:
    if not valor:
        return None
    tipos = [t.strip() for t in valor.split(",") if t.strip()]
    desconocidos = sorted(set(tipos) - set(TIPOS_EVENTO))
    if desconocidos:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Tipo de evento desconocido: {', '.join(desconocidos)}",
        )
    return tipos


@router.get("", response_model=PaginaActividad)
def listar_actividad(
    ronda: int | None = Query(default=None),
    usuario: str | None = Query(default=None, max_length=200),
    tipo: str | None = Query(default=None, max_length=200),
    antes: str | None = Query(default=None, max_length=120),
    limite: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    proyecto: Proyecto = Depends(proyecto_actual),
    _actor: Actor = Depends(SEGUIMIENTO),
) -> PaginaActividad:
    return actividad.listar(
        db,
        contenido.obtener(proyecto),
        proyecto,
        limite,
        tipos=_tipos(tipo),
        usuario=usuario or None,
        ronda=ronda,
        antes=antes,
    )


@router.get("/resumen", response_model=ResumenPresencia)
def resumen_actividad(
    db: Session = Depends(get_db),
    proyecto: Proyecto = Depends(proyecto_actual),
    actor: Actor = Depends(SEGUIMIENTO),
) -> ResumenPresencia:
    presentes = presencia.listar(db, contenido.obtener(proyecto), actor.email, proyecto.id)
    return presencia.resumir(presentes)
