import logging
import threading
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import engine
from app.models.contenido import ContenidoProcedimiento, ContenidoSeccion
from app.schemas.contenido import Procedimiento, Seccion
from app.services import contenido_media as medias
from app.services import contenido_versiones as versiones
from app.services import instancia as instancias
from app.services import proyectos
from app.services.contenido import Armado, Contenido

logger = logging.getLogger("validacion.contenido")


def _firma_instancia() -> tuple:
    ruta = instancias.ruta_de(Path(settings.contenido_dir))
    return (str(ruta), ruta.stat().st_mtime_ns) if ruta.is_file() else ()


def construir(db: Session, proyecto_id: int) -> Contenido:
    armado = Armado(errores=[])
    instancia = instancias.leer(Path(settings.contenido_dir), armado.errores)
    urls = medias.urls(db, proyecto_id)
    filas = db.scalars(
        select(ContenidoSeccion)
        .where(ContenidoSeccion.proyecto_id == proyecto_id)
        .order_by(ContenidoSeccion.orden, ContenidoSeccion.id)
    )
    for fila in filas:
        try:
            seccion = Seccion.model_validate(fila.datos)
        except ValidationError as error:
            armado.errores.append(f"{fila.id}: {error}")
            continue
        if not seccion.oculta:
            armado.agregar(urls.get, seccion)
    orden = (ContenidoProcedimiento.orden, ContenidoProcedimiento.id)
    consulta = select(ContenidoProcedimiento).where(
        ContenidoProcedimiento.proyecto_id == proyecto_id
    )
    for fila in db.scalars(consulta.order_by(*orden)):
        try:
            procedimiento = Procedimiento.model_validate(fila.datos)
        except ValidationError as error:
            armado.errores.append(f"procedimiento {fila.id}: {error}")
            continue
        procedimiento.url = urls.get(procedimiento.id)
        armado.procedimientos[procedimiento.id] = procedimiento
    return armado.terminar(instancia)


class CacheDeBase:
    def __init__(self, motor: Engine | None = None) -> None:
        self._motor = motor
        self._guardados: dict[int, tuple[tuple, Contenido]] = {}
        self._candado = threading.Lock()

    @property
    def motor(self) -> Engine:
        return self._motor or engine

    def _resolver(self, db: Session, proyecto_id: int | None) -> int:
        return proyecto_id if proyecto_id is not None else proyectos.por_omision(db).id

    def obtener(self, proyecto_id: int | None = None) -> Contenido:
        with Session(self.motor) as db:
            proyecto_id = self._resolver(db, proyecto_id)
            marca = versiones.ultima(db, proyecto_id), _firma_instancia()
        with self._candado:
            guardado = self._guardados.get(proyecto_id)
            if guardado is not None and guardado[0] == marca:
                return guardado[1]
            with Session(self.motor) as db:
                contenido = construir(db, proyecto_id)
            self._guardados[proyecto_id] = (marca, contenido)
            return contenido

    def olvidar(self) -> None:
        with self._candado:
            self._guardados.clear()


cache = CacheDeBase()


def cargar(proyecto_id: int | None = None) -> Contenido:
    return cache.obtener(proyecto_id)
