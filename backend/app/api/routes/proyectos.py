from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import Actor, get_actor, require_permission
from app.core.database import get_db
from app.core.permisos import ADMINISTRAR
from app.models.proyecto import Proyecto
from app.schemas.proyecto import (
    OrdenProyectos,
    ProyectoCambios,
    ProyectoCrear,
    ProyectoItem,
    ProyectosAdmin,
)
from app.services import proyectos
from app.services import proyectos_admin as gestion

router = APIRouter(tags=["proyectos"])

admin = require_permission(ADMINISTRAR)


@router.get("/api/proyectos", response_model=list[ProyectoItem])
def listar(db: Session = Depends(get_db), _actor: Actor = Depends(get_actor)) -> list[Proyecto]:
    proyectos.asegurar_por_omision(db)
    return proyectos.ordenados(db)


@router.get("/api/admin/proyectos", response_model=ProyectosAdmin)
def estado(db: Session = Depends(get_db), _actor: Actor = Depends(admin)) -> ProyectosAdmin:
    return gestion.estado(db)


@router.post(
    "/api/admin/proyectos", response_model=ProyectoItem, status_code=status.HTTP_201_CREATED
)
def crear(
    datos: ProyectoCrear, db: Session = Depends(get_db), _actor: Actor = Depends(admin)
) -> Proyecto:
    return gestion.crear(db, datos)


@router.put("/api/admin/proyectos/orden", status_code=status.HTTP_204_NO_CONTENT)
def ordenar(
    orden: OrdenProyectos, db: Session = Depends(get_db), _actor: Actor = Depends(admin)
) -> None:
    gestion.ordenar(db, orden.ids)


@router.patch("/api/admin/proyectos/{proyecto_id}", response_model=ProyectoItem)
def actualizar(
    proyecto_id: int,
    cambios: ProyectoCambios,
    db: Session = Depends(get_db),
    _actor: Actor = Depends(admin),
) -> Proyecto:
    return gestion.actualizar(db, proyectos.obtener_o_404(db, proyecto_id), cambios)


@router.delete("/api/admin/proyectos/{proyecto_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar(proyecto_id: int, db: Session = Depends(get_db), _actor: Actor = Depends(admin)) -> None:
    gestion.borrar(db, proyectos.obtener_o_404(db, proyecto_id))
