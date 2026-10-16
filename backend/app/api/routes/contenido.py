from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.deps import Actor, get_actor, lectura_o_permiso, proyecto_actual
from app.core.database import get_db
from app.core.permisos import EDITAR_CONTENIDO
from app.models.proyecto import Proyecto
from app.schemas.contenido import ContenidoResponse
from app.services import contenido
from app.services.contenido_exportacion import exportar

router = APIRouter(prefix="/api/contenido", tags=["contenido"])


@router.get("", response_model=ContenidoResponse)
def obtener_contenido(
    proyecto: Proyecto = Depends(proyecto_actual), _actor: Actor = Depends(get_actor)
) -> ContenidoResponse:
    return contenido.obtener(proyecto).respuesta


@router.get("/exportar.zip")
def exportar_contenido(
    db: Session = Depends(get_db),
    proyecto: Proyecto = Depends(proyecto_actual),
    _actor: Actor = Depends(lectura_o_permiso(EDITAR_CONTENIDO)),
) -> Response:
    nombre = "contenido.zip" if proyecto.por_omision else f"contenido-{proyecto.clave}.zip"
    return Response(
        content=exportar(db, proyecto.id),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{nombre}"',
            "Cache-Control": "no-store",
        },
    )
