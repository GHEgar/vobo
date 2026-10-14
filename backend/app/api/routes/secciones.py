from typing import Literal

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import Actor, require_permission
from app.core.database import get_db
from app.core.permisos import EJECUTAR_CASOS
from app.schemas.seccion import SeccionResultadoResponse
from app.services import contenido, evidencias, secciones

router = APIRouter(prefix="/api/secciones", tags=["secciones"])


@router.post("/{seccion_id}/resultado", response_model=SeccionResultadoResponse)
async def marcar_seccion(
    seccion_id: str,
    ronda_id: int = Form(...),
    estado: Literal["pasa", "falla"] = Form(...),
    obtenido: str | None = Form(default=None, max_length=2000),
    sobrescribir: bool = Form(default=False),
    navegador: str = Form(default=""),
    url: str = Form(default=""),
    imagenes: list[UploadFile] = File(default_factory=list),
    db: Session = Depends(get_db),
    actor: Actor = Depends(require_permission(EJECUTAR_CASOS)),
) -> SeccionResultadoResponse:
    leidas = await evidencias.leer(imagenes) if estado == "falla" else []
    datos = secciones.VeredictoSeccion(
        ronda_id=ronda_id,
        seccion_id=seccion_id,
        estado=estado,
        obtenido=obtenido,
        sobrescribir=sobrescribir,
        navegador=navegador,
        url=url,
        tecnico=actor.ve("tecnico"),
    )
    return secciones.aplicar(db, contenido.obtener(), actor.email, datos, leidas)
