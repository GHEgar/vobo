from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.falla import SEVERIDADES, Evidencia, Falla
from app.schemas.seccion import SeccionResultadoResponse
from app.services import evidencias, resultados, rondas
from app.services.contenido import Contenido
from app.services.visibilidad import secciones_visibles

PREFIJO_SECCION = "Toda la sección: "


@dataclass(frozen=True)
class VeredictoSeccion:
    ronda_id: int
    seccion_id: str
    estado: str
    obtenido: str | None
    sobrescribir: bool
    navegador: str = ""
    url: str = ""
    tecnico: bool = False


def _casos_visibles(db: Session, contenido: Contenido, email: str, datos: VeredictoSeccion) -> list:
    seccion = next((s for s in contenido.respuesta.secciones if s.id == datos.seccion_id), None)
    if seccion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sección no encontrada")
    asignadas = set(rondas.secciones_asignadas(db, datos.ronda_id, email))
    if seccion.id not in secciones_visibles(contenido, asignadas, datos.tecnico):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="La sección no está asignada a tu cuenta"
        )
    return seccion.casos


def _crear_falla(
    db: Session, email: str, datos: VeredictoSeccion, casos: list, imagenes: list
) -> Falla:
    severidad = min((c.severidad for c in casos), key=SEVERIDADES.index)
    falla = Falla(
        ronda_id=datos.ronda_id,
        caso_id=casos[0].id,
        seccion_id=datos.seccion_id,
        usuario_email=email,
        paso=None,
        obtenido=f"{PREFIJO_SECCION}{(datos.obtenido or '').strip()}",
        reproducible="siempre",
        severidad=severidad,
        navegador=datos.navegador[:400],
        url=datos.url[:500],
    )
    db.add(falla)
    db.flush()
    for contenido_imagen, mime, extension in imagenes:
        ruta = evidencias.guardar(falla.id, contenido_imagen, extension)
        db.add(Evidencia(falla_id=falla.id, ruta=ruta, mime=mime))
    return falla


def aplicar(
    db: Session,
    contenido: Contenido,
    email: str,
    datos: VeredictoSeccion,
    imagenes: list[tuple[bytes, str, str]],
) -> SeccionResultadoResponse:
    rondas.abierta_o_409(db, datos.ronda_id)
    if datos.estado == "falla" and not (datos.obtenido or "").strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Describe qué está mal en la sección"
        )
    casos = _casos_visibles(db, contenido, email, datos)
    actuales = {r.caso_id: r.estado for r in resultados.de_usuario(db, datos.ronda_id, email)}
    objetivo = [
        c for c in casos if datos.sobrescribir or actuales.get(c.id, "pendiente") == "pendiente"
    ]
    falla = None
    if objetivo and datos.estado == "falla":
        falla = _crear_falla(db, email, datos, objetivo, imagenes)
    for caso in objetivo:
        pasos = None
        if datos.estado == "pasa":
            pasos = [
                {"paso": i, "estado": "pasa", "comentario": None} for i in range(len(caso.pasos))
            ]
        resultados.guardar(db, datos.ronda_id, caso.id, email, datos.estado, pasos)
    db.commit()
    return SeccionResultadoResponse(
        afectados=len(objetivo),
        omitidos=len(casos) - len(objetivo),
        falla_id=falla.id if falla else None,
    )
