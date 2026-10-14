from typing import Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import Actor, lectura_o_permiso, require_permission
from app.core.database import get_db
from app.core.permisos import EJECUTAR_CASOS, GESTIONAR_FALLAS
from app.schemas.falla import EstadoFalla, FallaResponse, FallaUpdate, Reproducible, TipoFalla
from app.services import contenido, evidencias, fallas, rondas

router = APIRouter(prefix="/api/fallas", tags=["fallas"])

SeveridadFiltro = Literal["critica", "alta", "media", "baja"]


@router.get("", response_model=list[FallaResponse])
def listar_fallas(
    ronda: int | None = Query(default=None),
    sistema: str | None = Query(default=None),
    severidad: SeveridadFiltro | None = Query(default=None),
    estado: EstadoFalla | None = Query(default=None),
    tipo: TipoFalla | None = Query(default=None),
    db: Session = Depends(get_db),
    _actor: Actor = Depends(lectura_o_permiso(GESTIONAR_FALLAS, "fallas")),
) -> list[FallaResponse]:
    actual = contenido.obtener()
    filtro = fallas.FiltroFallas(
        ronda=ronda, sistema=sistema, severidad=severidad, estado=estado, tipo=tipo
    )
    return [fallas.serializar(f, actual) for f in fallas.listar(db, actual, filtro)]


@router.post("", response_model=FallaResponse, status_code=status.HTTP_201_CREATED)
async def reportar_falla(
    ronda_id: int = Form(...),
    caso_id: str = Form(...),
    obtenido: str = Form(..., min_length=3, max_length=4000),
    reproducible: Reproducible | None = Form(default=None),
    tipo: TipoFalla = Form(default="falla"),
    paso: int | None = Form(default=None),
    navegador: str = Form(default=""),
    url: str = Form(default=""),
    version_visible: str = Form(default=""),
    imagenes: list[UploadFile] = File(default_factory=list),
    db: Session = Depends(get_db),
    actor: Actor = Depends(require_permission(EJECUTAR_CASOS)),
) -> FallaResponse:
    if tipo == "falla" and reproducible is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Indica si la falla se repite"
        )
    actual = contenido.obtener()
    rondas.abierta_o_409(db, ronda_id)
    leidas = await evidencias.leer(imagenes)
    datos = fallas.NuevaFalla(
        ronda_id=ronda_id,
        caso_id=caso_id,
        paso=paso,
        obtenido=obtenido,
        reproducible=reproducible or "una_vez",
        tipo=tipo,
        navegador=navegador,
        url=url,
        version_visible=version_visible,
    )
    falla = fallas.crear(db, actual, actor.email, datos, leidas)
    return fallas.serializar(falla, actual)


@router.patch("/{falla_id}", response_model=FallaResponse)
def actualizar_falla(
    falla_id: int,
    cambios: FallaUpdate,
    db: Session = Depends(get_db),
    _actor: Actor = Depends(require_permission(GESTIONAR_FALLAS)),
) -> FallaResponse:
    falla = fallas.actualizar(db, falla_id, cambios)
    return fallas.serializar(falla, contenido.obtener())
