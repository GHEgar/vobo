from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.time import utcnow
from app.models.contenido import ContenidoMedia, ContenidoProcedimiento, ContenidoSeccion
from app.schemas.editor import MediaInfo, ProcedimientoDetalle
from app.services import contenido_media as medias
from app.services import contenido_validacion as validacion
from app.services import contenido_versiones as versiones


def procedimiento_o_404(
    db: Session, proyecto_id: int, procedimiento_id: str
) -> ContenidoProcedimiento:
    fila = db.get(ContenidoProcedimiento, {"proyecto_id": proyecto_id, "id": procedimiento_id})
    if fila is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Procedimiento no encontrado"
        )
    return fila


def _referidos(datos: dict) -> set[str]:
    propios = {m.get("procedimiento") for m in datos.get("media") or []}
    for caso in datos.get("casos") or []:
        propios |= {p.get("procedimiento") for p in caso.get("pasos") or []}
    return propios - {None}


def usos(db: Session, proyecto_id: int) -> dict[str, list[str]]:
    resultado: dict[str, list[str]] = {}
    consulta = select(ContenidoSeccion.id, ContenidoSeccion.datos).where(
        ContenidoSeccion.proyecto_id == proyecto_id
    )
    for seccion_id, datos in db.execute(consulta):
        for procedimiento in _referidos(datos):
            resultado.setdefault(procedimiento, []).append(seccion_id)
    return {k: sorted(v) for k, v in resultado.items()}


def _media(media: ContenidoMedia | None) -> MediaInfo | None:
    if media is None:
        return None
    return MediaInfo(
        archivo=media.archivo,
        mime=media.mime,
        tamano=media.tamano,
        url=medias.url_de(media),
        subido=media.subido,
        autor_email=media.autor_email,
    )


def detalle(
    db: Session, fila: ContenidoProcedimiento, usados: dict[str, list[str]] | None = None
) -> ProcedimientoDetalle:
    usados = usos(db, fila.proyecto_id) if usados is None else usados
    return ProcedimientoDetalle(
        id=fila.id,
        datos=fila.datos,
        actualizado=fila.actualizado,
        autor_email=fila.autor_email,
        media=_media(medias.de(db, fila.proyecto_id, fila.id)),
        usos=usados.get(fila.id, []),
    )


def listar(db: Session, proyecto_id: int) -> list[ProcedimientoDetalle]:
    usados = usos(db, proyecto_id)
    orden = (ContenidoProcedimiento.orden, ContenidoProcedimiento.id)
    consulta = select(ContenidoProcedimiento).where(
        ContenidoProcedimiento.proyecto_id == proyecto_id
    )
    return [detalle(db, f, usados) for f in db.scalars(consulta.order_by(*orden))]


def _escribir(
    db: Session, fila: ContenidoProcedimiento, datos: dict, autor: str
) -> ContenidoProcedimiento:
    fila.datos = datos
    fila.actualizado = utcnow()
    fila.autor_email = autor
    db.commit()
    return fila


def crear(
    db: Session, proyecto_id: int, datos: dict, autor: str, accion: str = "crear"
) -> ContenidoProcedimiento:
    validado = validacion.procedimiento(datos)
    clave = {"proyecto_id": proyecto_id, "id": validado.id}
    if db.get(ContenidoProcedimiento, clave) is not None:
        raise validacion.invalido(
            [validacion.error(["id"], "Ya existe un procedimiento con ese id")]
        )
    maximo = select(func.max(ContenidoProcedimiento.orden)).where(
        ContenidoProcedimiento.proyecto_id == proyecto_id
    )
    fila = ContenidoProcedimiento(**clave, orden=(db.scalar(maximo) or 0) + 1)
    db.add(fila)
    versiones.registrar(db, proyecto_id, "procedimiento", validado.id, accion, None, autor)
    return _escribir(db, fila, validacion.normalizar_procedimiento(validado), autor)


def guardar(
    db: Session, fila: ContenidoProcedimiento, datos: dict, autor: str, accion: str = "editar"
) -> ContenidoProcedimiento:
    if datos.get("id") != fila.id:
        raise validacion.invalido([validacion.error(["id"], "El id del procedimiento no cambia")])
    nuevos = validacion.normalizar_procedimiento(validacion.procedimiento(datos))
    if nuevos == fila.datos:
        return fila
    versiones.registrar(db, fila.proyecto_id, "procedimiento", fila.id, accion, fila.datos, autor)
    return _escribir(db, fila, nuevos, autor)


def borrar(db: Session, fila: ContenidoProcedimiento, autor: str) -> None:
    usado = usos(db, fila.proyecto_id).get(fila.id)
    if usado:
        raise validacion.conflicto([f"Lo usan las secciones {', '.join(usado)}; quítalo primero"])
    versiones.registrar(db, fila.proyecto_id, "procedimiento", fila.id, "borrar", fila.datos, autor)
    medias.borrar(db, fila.proyecto_id, fila.id, autor)
    db.delete(fila)
    db.commit()


def subir_media(
    db: Session, fila: ContenidoProcedimiento, archivo: medias.Archivo, autor: str
) -> None:
    medias.guardar(db, fila.proyecto_id, fila.id, archivo, autor)
    db.commit()


def quitar_media(db: Session, fila: ContenidoProcedimiento, autor: str) -> None:
    medias.borrar(db, fila.proyecto_id, fila.id, autor)
    db.commit()
