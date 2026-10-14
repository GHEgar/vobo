from fastapi import APIRouter, Depends

from app.api.deps import Actor, get_actor
from app.schemas.contenido import ContenidoResponse
from app.services import contenido

router = APIRouter(prefix="/api/contenido", tags=["contenido"])


@router.get("", response_model=ContenidoResponse)
def obtener_contenido(_actor: Actor = Depends(get_actor)) -> ContenidoResponse:
    return contenido.obtener().respuesta
