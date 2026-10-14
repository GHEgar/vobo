from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import Actor, get_actor, require_permission
from app.core.database import get_db
from app.core.permisos import GESTIONAR_FALLAS
from app.models.ronda import Asignacion, Ronda
from app.models.usuario import Usuario
from app.schemas.ronda import (
    AsignacionItem,
    AsignacionResponse,
    RondaCreate,
    RondaResponse,
    RondaUpdate,
    UsuarioConocido,
)
from app.services import contenido, rondas

router = APIRouter(prefix="/api/rondas", tags=["rondas"])


@router.get("", response_model=list[RondaResponse])
def listar_rondas(db: Session = Depends(get_db), _actor: Actor = Depends(get_actor)) -> list[Ronda]:
    return list(db.scalars(select(Ronda).order_by(Ronda.creada.desc(), Ronda.id.desc())))


@router.get("/usuarios", response_model=list[UsuarioConocido])
def listar_usuarios(
    db: Session = Depends(get_db),
    _actor: Actor = Depends(require_permission(GESTIONAR_FALLAS)),
) -> list[Usuario]:
    return list(db.scalars(select(Usuario).order_by(Usuario.nombre)))


@router.get("/{ronda_id}/asignaciones", response_model=list[AsignacionResponse])
def listar_asignaciones(
    ronda_id: int,
    db: Session = Depends(get_db),
    _actor: Actor = Depends(require_permission(GESTIONAR_FALLAS)),
) -> list[Asignacion]:
    rondas.obtener_o_404(db, ronda_id)
    consulta = select(Asignacion).where(Asignacion.ronda_id == ronda_id)
    return list(db.scalars(consulta.order_by(Asignacion.usuario_email, Asignacion.seccion_id)))


@router.post("", response_model=RondaResponse, status_code=status.HTTP_201_CREATED)
def crear_ronda(
    datos: RondaCreate,
    db: Session = Depends(get_db),
    _actor: Actor = Depends(require_permission(GESTIONAR_FALLAS)),
) -> Ronda:
    ronda = Ronda(nombre=datos.nombre.strip(), snapshot=datos.snapshot.strip(), abierta=True)
    db.add(ronda)
    db.commit()
    db.refresh(ronda)
    return ronda


@router.patch("/{ronda_id}", response_model=RondaResponse)
def actualizar_ronda(
    ronda_id: int,
    cambios: RondaUpdate,
    db: Session = Depends(get_db),
    _actor: Actor = Depends(require_permission(GESTIONAR_FALLAS)),
) -> Ronda:
    ronda = rondas.obtener_o_404(db, ronda_id)
    for campo, valor in cambios.model_dump(exclude_none=True).items():
        setattr(ronda, campo, valor.strip() if isinstance(valor, str) else valor)
    db.commit()
    db.refresh(ronda)
    return ronda


@router.delete("/{ronda_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_ronda(
    ronda_id: int,
    db: Session = Depends(get_db),
    _actor: Actor = Depends(require_permission(GESTIONAR_FALLAS)),
) -> None:
    rondas.borrar(db, rondas.obtener_o_404(db, ronda_id))


@router.put("/{ronda_id}/asignaciones", response_model=list[AsignacionResponse])
def reemplazar_asignaciones(
    ronda_id: int,
    items: list[AsignacionItem],
    db: Session = Depends(get_db),
    _actor: Actor = Depends(require_permission(GESTIONAR_FALLAS)),
) -> list[Asignacion]:
    ronda = rondas.obtener_o_404(db, ronda_id)
    validas = {s.id for s in contenido.obtener().respuesta.secciones}
    return rondas.reemplazar_asignaciones(db, ronda, items, validas)
