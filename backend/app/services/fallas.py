from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.falla import Evidencia, Falla
from app.models.ronda import Ronda
from app.schemas.falla import EvidenciaResponse, FallaResponse, FallaUpdate
from app.services import evidencias, resultados
from app.services.contenido import Contenido, caso_o_404


@dataclass(frozen=True)
class NuevaFalla:
    ronda_id: int
    caso_id: str
    paso: int | None
    obtenido: str
    reproducible: str
    navegador: str
    url: str
    version_visible: str
    tipo: str = "falla"


@dataclass(frozen=True)
class FiltroFallas:
    ronda: int | None = None
    sistema: str | None = None
    severidad: str | None = None
    estado: str | None = None
    tipo: str | None = None
    proyecto_id: int | None = None


def crear(
    db: Session,
    contenido: Contenido,
    email: str,
    datos: NuevaFalla,
    imagenes: list[tuple[bytes, str, str]],
) -> Falla:
    ubicado = caso_o_404(contenido, datos.caso_id)
    if datos.paso is not None and not 0 <= datos.paso < len(ubicado.caso.pasos):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Paso inexistente")
    falla = Falla(
        ronda_id=datos.ronda_id,
        caso_id=datos.caso_id,
        usuario_email=email,
        paso=datos.paso,
        obtenido=datos.obtenido.strip(),
        reproducible=datos.reproducible,
        severidad=ubicado.caso.severidad,
        navegador=datos.navegador[:400],
        url=datos.url[:500],
        version_visible=datos.version_visible[:120],
        tipo=datos.tipo,
    )
    db.add(falla)
    db.flush()
    for contenido_imagen, mime, extension in imagenes:
        ruta = evidencias.guardar(falla.id, contenido_imagen, extension)
        db.add(Evidencia(falla_id=falla.id, ruta=ruta, mime=mime))
    estado = "no_pude" if datos.tipo == "no_pude" else "falla"
    resultados.guardar(db, datos.ronda_id, datos.caso_id, email, estado)
    db.commit()
    db.refresh(falla)
    return falla


def listar(db: Session, contenido: Contenido, filtro: FiltroFallas) -> list[Falla]:
    consulta = select(Falla).options(selectinload(Falla.evidencias)).order_by(Falla.creada.desc())
    if filtro.ronda is not None:
        consulta = consulta.where(Falla.ronda_id == filtro.ronda)
    elif filtro.proyecto_id is not None:
        del_proyecto = select(Ronda.id).where(Ronda.proyecto_id == filtro.proyecto_id)
        consulta = consulta.where(Falla.ronda_id.in_(del_proyecto))
    if filtro.severidad:
        consulta = consulta.where(Falla.severidad == filtro.severidad)
    if filtro.estado:
        consulta = consulta.where(Falla.estado == filtro.estado)
    if filtro.tipo:
        consulta = consulta.where(Falla.tipo == filtro.tipo)
    if filtro.sistema:
        casos = [cid for cid, u in contenido.casos.items() if u.sistema == filtro.sistema]
        consulta = consulta.where(Falla.caso_id.in_(casos))
    return list(db.scalars(consulta).all())


def actualizar(db: Session, falla_id: int, cambios: FallaUpdate) -> Falla:
    falla = db.get(Falla, falla_id)
    if falla is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Falla no encontrada")
    if cambios.estado is not None:
        falla.estado = cambios.estado
    if cambios.nota_resolucion is not None:
        falla.nota_resolucion = cambios.nota_resolucion.strip()
    db.commit()
    db.refresh(falla)
    return falla


def _titulo_seccion(contenido: Contenido, seccion_id: str) -> str:
    return next((s.titulo for s in contenido.respuesta.secciones if s.id == seccion_id), "")


def serializar(falla: Falla, contenido: Contenido) -> FallaResponse:
    ubicado = contenido.casos.get(falla.caso_id)
    caso = ubicado.caso if ubicado else None
    paso_texto = ""
    if caso is not None and falla.paso is not None and falla.paso < len(caso.pasos):
        paso_texto = caso.pasos[falla.paso].texto
    return FallaResponse(
        id=falla.id,
        ronda_id=falla.ronda_id,
        caso_id=falla.caso_id,
        caso_titulo=caso.titulo if caso else "",
        seccion_id=falla.seccion_id or (ubicado.seccion_id if ubicado else ""),
        seccion_titulo=_titulo_seccion(
            contenido, falla.seccion_id or (ubicado.seccion_id if ubicado else "")
        ),
        seccion_completa=falla.seccion_id is not None,
        tipo=falla.tipo or "falla",
        sistema=ubicado.sistema if ubicado else "",
        familia=caso.familia if caso else "",
        usuario_email=falla.usuario_email,
        paso=falla.paso,
        paso_texto=paso_texto,
        obtenido=falla.obtenido,
        reproducible=falla.reproducible,
        severidad=falla.severidad,
        navegador=falla.navegador,
        url=falla.url,
        version_visible=falla.version_visible,
        creada=falla.creada,
        estado=falla.estado,
        nota_resolucion=falla.nota_resolucion,
        evidencias=[
            EvidenciaResponse(id=e.id, mime=e.mime, url=f"/api/evidencias/{e.id}")
            for e in falla.evidencias
        ],
    )
