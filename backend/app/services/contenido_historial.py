from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.contenido import ContenidoProcedimiento, ContenidoSeccion, ContenidoVersion
from app.services import contenido_editor as editor
from app.services import contenido_procedimientos as procedimientos
from app.services import contenido_validacion as validacion
from app.services import contenido_versiones as versiones

RESTAURABLES = {"seccion": ContenidoSeccion, "procedimiento": ContenidoProcedimiento}


def historial(db: Session, proyecto_id: int, tipo: str, objeto_id: str) -> list[ContenidoVersion]:
    if tipo not in versiones.TIPOS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo desconocido")
    propias = versiones.de(db, proyecto_id, tipo, objeto_id)
    if tipo == "procedimiento":
        medias = versiones.de(db, proyecto_id, "media", objeto_id)
        propias = sorted(propias + medias, key=lambda v: -v.id)
    return propias


def restaurar(db: Session, proyecto_id: int, version_id: int, autor: str) -> None:
    version = db.get(ContenidoVersion, version_id)
    if version is None or version.tipo not in RESTAURABLES or version.proyecto_id != proyecto_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Versión no encontrada")
    if version.datos is None:
        raise validacion.conflicto(["Esa versión es la creación; no hay un estado anterior"])
    datos = dict(version.datos)
    fila = db.get(RESTAURABLES[version.tipo], {"proyecto_id": proyecto_id, "id": version.objeto_id})
    if version.tipo == "seccion":
        if fila is None:
            editor.crear(db, proyecto_id, datos, autor, accion="restaurar")
        else:
            editor.guardar(db, fila, datos, autor, accion="restaurar")
    elif fila is None:
        procedimientos.crear(db, proyecto_id, datos, autor, accion="restaurar")
    else:
        procedimientos.guardar(db, fila, datos, autor, accion="restaurar")
