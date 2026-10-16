from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import Actor, proyecto_actual
from app.api.routes.editor import editar
from app.core.database import get_db
from app.models.contenido import ContenidoVersion
from app.models.proyecto import Proyecto
from app.schemas.editor import Documento, ProcedimientoDetalle, ResumenImportacion, VersionItem
from app.services import contenido_editor as editor
from app.services import contenido_historial as historial
from app.services import contenido_importacion as importacion
from app.services import contenido_media as medias
from app.services import contenido_procedimientos as procedimientos
from app.services import contenido_validacion as validacion
from app.services.contenido_paquete import MAX_ZIP, de_zip

router = APIRouter(
    prefix="/api/editor", tags=["editor"], dependencies=[Depends(editor.exigir_base)]
)


@router.get("/procedimientos", response_model=list[ProcedimientoDetalle])
def listar(
    db: Session = Depends(get_db),
    proyecto: Proyecto = Depends(proyecto_actual),
    _actor: Actor = Depends(editar),
) -> list[ProcedimientoDetalle]:
    return procedimientos.listar(db, proyecto.id)


@router.post(
    "/procedimientos", response_model=ProcedimientoDetalle, status_code=status.HTTP_201_CREATED
)
def crear(
    documento: Documento,
    db: Session = Depends(get_db),
    proyecto: Proyecto = Depends(proyecto_actual),
    actor: Actor = Depends(editar),
) -> ProcedimientoDetalle:
    fila = procedimientos.crear(db, proyecto.id, documento.datos, actor.email)
    return procedimientos.detalle(db, fila)


@router.put("/procedimientos/{procedimiento_id}", response_model=ProcedimientoDetalle)
def guardar(
    procedimiento_id: str,
    documento: Documento,
    db: Session = Depends(get_db),
    proyecto: Proyecto = Depends(proyecto_actual),
    actor: Actor = Depends(editar),
) -> ProcedimientoDetalle:
    fila = procedimientos.procedimiento_o_404(db, proyecto.id, procedimiento_id)
    return procedimientos.detalle(
        db, procedimientos.guardar(db, fila, documento.datos, actor.email)
    )


@router.delete("/procedimientos/{procedimiento_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar(
    procedimiento_id: str,
    db: Session = Depends(get_db),
    proyecto: Proyecto = Depends(proyecto_actual),
    actor: Actor = Depends(editar),
) -> None:
    fila = procedimientos.procedimiento_o_404(db, proyecto.id, procedimiento_id)
    procedimientos.borrar(db, fila, actor.email)


@router.put("/procedimientos/{procedimiento_id}/media", response_model=ProcedimientoDetalle)
async def subir_media(
    procedimiento_id: str,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    proyecto: Proyecto = Depends(proyecto_actual),
    actor: Actor = Depends(editar),
) -> ProcedimientoDetalle:
    fila = procedimientos.procedimiento_o_404(db, proyecto.id, procedimiento_id)
    leido = medias.validar(await archivo.read(medias.MAX_BYTES + 1), archivo.filename or "")
    procedimientos.subir_media(db, fila, leido, actor.email)
    return procedimientos.detalle(db, fila)


@router.delete("/procedimientos/{procedimiento_id}/media", response_model=ProcedimientoDetalle)
def quitar_media(
    procedimiento_id: str,
    db: Session = Depends(get_db),
    proyecto: Proyecto = Depends(proyecto_actual),
    actor: Actor = Depends(editar),
) -> ProcedimientoDetalle:
    fila = procedimientos.procedimiento_o_404(db, proyecto.id, procedimiento_id)
    procedimientos.quitar_media(db, fila, actor.email)
    return procedimientos.detalle(db, fila)


@router.get("/historial/{tipo}/{objeto_id}", response_model=list[VersionItem])
def ver_historial(
    tipo: str,
    objeto_id: str,
    db: Session = Depends(get_db),
    proyecto: Proyecto = Depends(proyecto_actual),
    _actor: Actor = Depends(editar),
) -> list[ContenidoVersion]:
    return historial.historial(db, proyecto.id, tipo, objeto_id)


@router.post("/historial/{version_id}/restaurar", status_code=status.HTTP_204_NO_CONTENT)
def restaurar(
    version_id: int,
    db: Session = Depends(get_db),
    proyecto: Proyecto = Depends(proyecto_actual),
    actor: Actor = Depends(editar),
) -> None:
    historial.restaurar(db, proyecto.id, version_id, actor.email)


@router.post("/importar", response_model=ResumenImportacion)
async def importar(
    archivo: UploadFile = File(...),
    confirmar: bool = Query(default=False),
    db: Session = Depends(get_db),
    proyecto: Proyecto = Depends(proyecto_actual),
    actor: Actor = Depends(editar),
) -> ResumenImportacion:
    contenido = await archivo.read(MAX_ZIP + 1)
    if len(contenido) > MAX_ZIP:
        raise validacion.conflicto(["El .zip pesa más de 200 MB"])
    paquete = de_zip(contenido)
    if paquete.errores:
        raise validacion.invalido([validacion.error(["archivo"], e) for e in paquete.errores])
    plan = importacion.planear(db, proyecto.id, paquete)
    aplicar = confirmar and not plan.bloqueos and not plan.sin_cambios
    if aplicar:
        importacion.aplicar(db, proyecto.id, paquete, plan, actor.email)
    return ResumenImportacion(
        aplicado=aplicar,
        sin_cambios=plan.sin_cambios,
        secciones=plan.secciones.__dict__,
        procedimientos=plan.procedimientos.__dict__,
        media=plan.media.__dict__,
        bloqueos=plan.bloqueos,
        ignorados=paquete.ignorados,
    )
