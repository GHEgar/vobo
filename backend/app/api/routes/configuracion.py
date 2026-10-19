from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import Actor, require_alguno, require_permission
from app.core.database import get_db
from app.core.permisos import EDITAR_CONFIGURACION, EDITAR_IDENTIDAD
from app.schemas.configuracion import ConfiguracionCambios, ConfiguracionResponse, Ranura
from app.services import configuracion, marca

router = APIRouter(prefix="/api/admin/configuracion", tags=["administracion"])

AJUSTES = frozenset({"proyectos", "cuentas"})
alguna = require_alguno(EDITAR_IDENTIDAD, EDITAR_CONFIGURACION)
identidad = require_permission(EDITAR_IDENTIDAD)


def _exigir_campos(actor: Actor, campos: set[str]) -> None:
    for campo in campos:
        permiso = EDITAR_CONFIGURACION if campo in AJUSTES else EDITAR_IDENTIDAD
        if not actor.puede(permiso):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=f"Requiere permiso: {permiso}"
            )


@router.get("", response_model=ConfiguracionResponse)
def ver(db: Session = Depends(get_db), _actor: Actor = Depends(alguna)) -> ConfiguracionResponse:
    return configuracion.estado(db)


@router.put("", response_model=ConfiguracionResponse)
def guardar(
    cambios: ConfiguracionCambios, db: Session = Depends(get_db), actor: Actor = Depends(alguna)
) -> ConfiguracionResponse:
    _exigir_campos(actor, set(cambios.model_fields_set))
    configuracion.guardar(db, cambios, actor.email)
    return configuracion.estado(db)


@router.put("/marca/{ranura}", response_model=ConfiguracionResponse)
async def subir_marca(
    ranura: Ranura,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    actor: Actor = Depends(identidad),
) -> ConfiguracionResponse:
    configuracion.subir(db, ranura, await archivo.read(marca.MAX_BYTES + 1), actor.email)
    return configuracion.estado(db)


@router.delete("/marca/{ranura}", response_model=ConfiguracionResponse)
def quitar_marca(
    ranura: Ranura, db: Session = Depends(get_db), _actor: Actor = Depends(identidad)
) -> ConfiguracionResponse:
    configuracion.quitar_archivo(db, ranura)
    return configuracion.estado(db)


@router.delete("/{clave}", response_model=ConfiguracionResponse, status_code=status.HTTP_200_OK)
def restablecer(
    clave: str, db: Session = Depends(get_db), actor: Actor = Depends(alguna)
) -> ConfiguracionResponse:
    _exigir_campos(actor, {clave})
    configuracion.restablecer(db, clave)
    return configuracion.estado(db)
