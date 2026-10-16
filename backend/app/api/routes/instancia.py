from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.proyecto import Proyecto
from app.schemas.instancia import InstanciaResponse, ProyectoPublico
from app.services import configuracion, marca, proyectos

router = APIRouter(prefix="/api/instancia", tags=["instancia"])


def _proyecto(db: Session, clave: str | None) -> Proyecto:
    if clave:
        try:
            return proyectos.de_clave(db, clave)
        except HTTPException:
            pass
    return proyectos.por_omision(db)


@router.get("", response_model=InstanciaResponse)
def obtener_instancia(
    proyecto: str | None = Query(default=None, max_length=60), db: Session = Depends(get_db)
) -> InstanciaResponse:
    elegido = _proyecto(db, proyecto)
    publico = ProyectoPublico.model_validate(elegido, from_attributes=True)
    return configuracion.respuesta(db).model_copy(update={"proyecto": publico})


@router.get("/tema.css")
def tema_css(db: Session = Depends(get_db)) -> Response:
    return Response(
        content=configuracion.css(db),
        media_type="text/css",
        headers={"Cache-Control": "no-cache", "X-Content-Type-Options": "nosniff"},
    )


@router.get("/marca/{nombre}")
def archivo_de_marca(
    nombre: str, v: str | None = Query(default=None), db: Session = Depends(get_db)
) -> Response:
    servido = configuracion.servir(db, nombre, v)
    if servido is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado")
    contenido, mime, vigente = servido
    return Response(content=contenido, media_type=mime, headers=marca.cabeceras(mime, vigente))
