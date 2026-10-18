import threading
import time

from sqlalchemy.orm import Session

from app.core.time import utcnow
from app.models.pantalla import Pantalla
from app.schemas.pantalla import DatosPantalla, MarcaPantalla, PantallaPublica
from app.services import configuracion, contenido, pantalla_personas, pantalla_proyectos

VIGENCIA = 15.0

_cache: dict[int, tuple[tuple, float, DatosPantalla]] = {}
_candado = threading.Lock()


def olvidar() -> None:
    with _candado:
        _cache.clear()


def marca(db: Session) -> MarcaPantalla:
    instancia = configuracion.respuesta(db)
    return MarcaPantalla(
        producto=instancia.producto,
        nombre=instancia.nombre,
        logo=instancia.logo.oscuro if instancia.logo else None,
        color_tema=instancia.color_tema,
    )


def publica(db: Session, pantalla: Pantalla) -> PantallaPublica:
    return PantallaPublica(
        nombre=pantalla.nombre,
        vistas=list(pantalla.vistas),
        segundos=pantalla.segundos,
        marca=marca(db),
    )


def calcular(db: Session, pantalla: Pantalla) -> DatosPantalla:
    fuentes = [
        pantalla_proyectos.fuente(db, proyecto, contenido.obtener(proyecto), color)
        for proyecto, color in pantalla_proyectos.elegidos(db, list(pantalla.proyectos or []))
    ]
    nombres = {s.clave: s.nombre for s in configuracion.respuesta(db).sistemas}
    return DatosPantalla(
        generado=utcnow(),
        proyectos=[pantalla_proyectos.resumen(db, f, nombres) for f in fuentes],
        personas=pantalla_personas.personas(db, fuentes),
        eventos=pantalla_personas.eventos(db, fuentes),
    )


def _firma(pantalla: Pantalla) -> tuple:
    return pantalla.token_hash, tuple(pantalla.proyectos or [])


def datos(db: Session, pantalla: Pantalla) -> DatosPantalla:
    firma = _firma(pantalla)
    ahora = time.monotonic()
    with _candado:
        guardado = _cache.get(pantalla.id)
        if guardado is not None and guardado[0] == firma and ahora - guardado[1] < VIGENCIA:
            return guardado[2]
        nuevos = calcular(db, pantalla)
        _cache[pantalla.id] = (firma, ahora, nuevos)
        return nuevos
