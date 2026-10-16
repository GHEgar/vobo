from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import Actor, proyecto_actual, require_permission
from app.core.config import settings
from app.core.database import get_db
from app.core.permisos import EDITAR_CONTENIDO
from app.models.proyecto import Proyecto
from app.schemas.editor import (
    Documento,
    Duplicado,
    EstadoEditor,
    Oculta,
    Orden,
    ProyectoPublico,
    SeccionDetalle,
    SeccionResumen,
)
from app.services import configuracion, contenido
from app.services import contenido_editor as editor

editar = require_permission(EDITAR_CONTENIDO)

router = APIRouter(prefix="/api/editor", tags=["editor"])
secciones = APIRouter(dependencies=[Depends(editor.exigir_base)])


@router.get("/estado", response_model=EstadoEditor)
def estado(
    proyecto: Proyecto = Depends(proyecto_actual), _actor: Actor = Depends(editar)
) -> EstadoEditor:
    actual = contenido.obtener(proyecto)
    sistemas = configuracion.efectiva().proyectos
    return EstadoEditor(
        fuente=settings.contenido_fuente,
        editable=settings.contenido_en_base,
        proyectos=sistemas,
        sistemas=sistemas,
        proyecto=ProyectoPublico.model_validate(proyecto, from_attributes=True),
        errores=actual.respuesta.errores,
    )


@secciones.get("/secciones", response_model=list[SeccionResumen])
def listar(
    db: Session = Depends(get_db),
    proyecto: Proyecto = Depends(proyecto_actual),
    _actor: Actor = Depends(editar),
) -> list[SeccionResumen]:
    return editor.listar(db, proyecto.id)


@secciones.post("/secciones", response_model=SeccionDetalle, status_code=status.HTTP_201_CREATED)
def crear(
    documento: Documento,
    db: Session = Depends(get_db),
    proyecto: Proyecto = Depends(proyecto_actual),
    actor: Actor = Depends(editar),
) -> SeccionDetalle:
    return editor.detalle(db, editor.crear(db, proyecto.id, documento.datos, actor.email))


@secciones.put("/secciones/orden", status_code=status.HTTP_204_NO_CONTENT)
def ordenar(
    orden: Orden,
    db: Session = Depends(get_db),
    proyecto: Proyecto = Depends(proyecto_actual),
    actor: Actor = Depends(editar),
) -> None:
    editor.ordenar(db, proyecto.id, orden.ids, actor.email)


@secciones.get("/secciones/{seccion_id}", response_model=SeccionDetalle)
def obtener(
    seccion_id: str,
    db: Session = Depends(get_db),
    proyecto: Proyecto = Depends(proyecto_actual),
    _actor: Actor = Depends(editar),
) -> SeccionDetalle:
    return editor.detalle(db, editor.seccion_o_404(db, proyecto.id, seccion_id))


@secciones.put("/secciones/{seccion_id}", response_model=SeccionDetalle)
def guardar(
    seccion_id: str,
    documento: Documento,
    db: Session = Depends(get_db),
    proyecto: Proyecto = Depends(proyecto_actual),
    actor: Actor = Depends(editar),
) -> SeccionDetalle:
    fila = editor.seccion_o_404(db, proyecto.id, seccion_id)
    return editor.detalle(db, editor.guardar(db, fila, documento.datos, actor.email))


@secciones.put("/secciones/{seccion_id}/oculta", response_model=SeccionDetalle)
def ocultar(
    seccion_id: str,
    datos: Oculta,
    db: Session = Depends(get_db),
    proyecto: Proyecto = Depends(proyecto_actual),
    actor: Actor = Depends(editar),
) -> SeccionDetalle:
    fila = editor.seccion_o_404(db, proyecto.id, seccion_id)
    return editor.detalle(db, editor.ocultar(db, fila, datos.oculta, actor.email))


@secciones.post(
    "/secciones/{seccion_id}/duplicar",
    response_model=SeccionDetalle,
    status_code=status.HTTP_201_CREATED,
)
def duplicar(
    seccion_id: str,
    datos: Duplicado,
    db: Session = Depends(get_db),
    proyecto: Proyecto = Depends(proyecto_actual),
    actor: Actor = Depends(editar),
) -> SeccionDetalle:
    fila = editor.seccion_o_404(db, proyecto.id, seccion_id)
    return editor.detalle(db, editor.duplicar(db, fila, datos.id, actor.email))


@secciones.delete("/secciones/{seccion_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar(
    seccion_id: str,
    db: Session = Depends(get_db),
    proyecto: Proyecto = Depends(proyecto_actual),
    actor: Actor = Depends(editar),
) -> None:
    editor.borrar(db, editor.seccion_o_404(db, proyecto.id, seccion_id), actor.email)


router.include_router(secciones)
