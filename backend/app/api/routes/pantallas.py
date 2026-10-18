from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import Actor, require_permission
from app.core.database import get_db
from app.core.permisos import ADMINISTRAR
from app.models.pantalla import Pantalla
from app.schemas.pantalla import (
    DatosPantalla,
    PantallaCambios,
    PantallaCrear,
    PantallaEnlace,
    PantallaItem,
    PantallaPublica,
)
from app.services import pantalla_datos, pantallas

router = APIRouter(tags=["pantallas"])

admin = require_permission(ADMINISTRAR)
SIN_CACHE = {"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"}


def _con_enlace(pantalla: Pantalla, enlace: str) -> PantallaEnlace:
    return PantallaEnlace(pantalla=PantallaItem.model_validate(pantalla), enlace=enlace)


@router.get("/api/admin/pantallas", response_model=list[PantallaItem])
def listar(db: Session = Depends(get_db), _actor: Actor = Depends(admin)) -> list[Pantalla]:
    return pantallas.listar(db)


@router.post(
    "/api/admin/pantallas", response_model=PantallaEnlace, status_code=status.HTTP_201_CREATED
)
def crear(
    datos: PantallaCrear, db: Session = Depends(get_db), actor: Actor = Depends(admin)
) -> PantallaEnlace:
    return _con_enlace(*pantallas.crear(db, datos, actor.email))


@router.patch("/api/admin/pantallas/{pantalla_id}", response_model=PantallaItem)
def actualizar(
    pantalla_id: int,
    cambios: PantallaCambios,
    db: Session = Depends(get_db),
    _actor: Actor = Depends(admin),
) -> Pantalla:
    return pantallas.actualizar(db, pantallas.obtener_o_404(db, pantalla_id), cambios)


@router.post("/api/admin/pantallas/{pantalla_id}/regenerar", response_model=PantallaEnlace)
def regenerar(
    pantalla_id: int, db: Session = Depends(get_db), _actor: Actor = Depends(admin)
) -> PantallaEnlace:
    return _con_enlace(*pantallas.regenerar(db, pantallas.obtener_o_404(db, pantalla_id)))


@router.delete("/api/admin/pantallas/{pantalla_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar(pantalla_id: int, db: Session = Depends(get_db), _actor: Actor = Depends(admin)) -> None:
    pantallas.borrar(db, pantallas.obtener_o_404(db, pantalla_id))


@router.get("/api/pantalla/{token}", response_model=PantallaPublica)
def configuracion(token: str, response: Response, db: Session = Depends(get_db)) -> PantallaPublica:
    pantalla = pantallas.vigente(db, token)
    pantallas.registrar_uso(db, pantalla)
    response.headers.update(SIN_CACHE)
    return pantalla_datos.publica(db, pantalla)


@router.get("/api/pantalla/{token}/datos", response_model=DatosPantalla)
def datos(token: str, response: Response, db: Session = Depends(get_db)) -> DatosPantalla:
    pantalla = pantallas.vigente(db, token)
    pantallas.registrar_uso(db, pantalla)
    response.headers.update(SIN_CACHE)
    return pantalla_datos.datos(db, pantalla)
