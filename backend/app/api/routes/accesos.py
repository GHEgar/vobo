from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import Actor, require_permission
from app.core.database import get_db
from app.core.permisos import GESTIONAR_FALLAS
from app.models.acceso import Acceso
from app.schemas.acceso import AccesoItem
from app.services import accesos

router = APIRouter(prefix="/api/accesos", tags=["accesos"])


@router.get("", response_model=list[AccesoItem])
def listar_accesos(
    db: Session = Depends(get_db),
    _actor: Actor = Depends(require_permission(GESTIONAR_FALLAS)),
) -> list[Acceso]:
    return accesos.listar(db)


@router.put("", response_model=list[AccesoItem])
def reemplazar_accesos(
    items: list[AccesoItem],
    db: Session = Depends(get_db),
    _actor: Actor = Depends(require_permission(GESTIONAR_FALLAS)),
) -> list[Acceso]:
    return accesos.reemplazar(db, items)
