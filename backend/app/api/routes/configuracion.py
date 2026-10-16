from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import Actor
from app.api.routes.admin import admin
from app.core.database import get_db
from app.schemas.configuracion import ConfiguracionCambios, ConfiguracionResponse, Ranura
from app.services import configuracion, marca

router = APIRouter(prefix="/api/admin/configuracion", tags=["administracion"])


@router.get("", response_model=ConfiguracionResponse)
def ver(db: Session = Depends(get_db), _actor: Actor = Depends(admin)) -> ConfiguracionResponse:
    return configuracion.estado(db)


@router.put("", response_model=ConfiguracionResponse)
def guardar(
    cambios: ConfiguracionCambios, db: Session = Depends(get_db), actor: Actor = Depends(admin)
) -> ConfiguracionResponse:
    configuracion.guardar(db, cambios, actor.email)
    return configuracion.estado(db)


@router.put("/marca/{ranura}", response_model=ConfiguracionResponse)
async def subir_marca(
    ranura: Ranura,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    actor: Actor = Depends(admin),
) -> ConfiguracionResponse:
    configuracion.subir(db, ranura, await archivo.read(marca.MAX_BYTES + 1), actor.email)
    return configuracion.estado(db)


@router.delete("/marca/{ranura}", response_model=ConfiguracionResponse)
def quitar_marca(
    ranura: Ranura, db: Session = Depends(get_db), _actor: Actor = Depends(admin)
) -> ConfiguracionResponse:
    configuracion.quitar_archivo(db, ranura)
    return configuracion.estado(db)


@router.delete("/{clave}", response_model=ConfiguracionResponse, status_code=status.HTTP_200_OK)
def restablecer(
    clave: str, db: Session = Depends(get_db), _actor: Actor = Depends(admin)
) -> ConfiguracionResponse:
    configuracion.restablecer(db, clave)
    return configuracion.estado(db)
