from fastapi import APIRouter

from app.schemas.instancia import InstanciaResponse
from app.services import contenido, instancia

router = APIRouter(prefix="/api/instancia", tags=["instancia"])


@router.get("", response_model=InstanciaResponse)
def obtener_instancia() -> InstanciaResponse:
    return instancia.respuesta(contenido.obtener().instancia)
