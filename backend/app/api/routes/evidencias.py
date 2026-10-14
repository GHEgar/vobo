from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import Actor, lectura_o_permiso
from app.core.database import get_db
from app.core.permisos import GESTIONAR_FALLAS
from app.models.falla import Evidencia
from app.services import evidencias

router = APIRouter(prefix="/api/evidencias", tags=["evidencias"])


@router.get("/{evidencia_id}")
def obtener_evidencia(
    evidencia_id: int,
    db: Session = Depends(get_db),
    _actor: Actor = Depends(lectura_o_permiso(GESTIONAR_FALLAS, "fallas")),
) -> FileResponse:
    evidencia = db.get(Evidencia, evidencia_id)
    ruta = evidencias.ruta_absoluta(evidencia.ruta) if evidencia else None
    if evidencia is None or ruta is None or not ruta.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidencia no encontrada")
    return FileResponse(
        ruta,
        media_type=evidencia.mime,
        headers={"Cache-Control": "private, max-age=3600", "X-Content-Type-Options": "nosniff"},
    )
