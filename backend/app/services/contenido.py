import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from fastapi import HTTPException, status
from pydantic import ValidationError

from app.core.config import settings
from app.models.proyecto import Proyecto
from app.schemas.contenido import (
    HERRAMIENTA_GENERAL,
    Caso,
    ContenidoResponse,
    Herramienta,
    Procedimiento,
    Seccion,
)
from app.schemas.instancia import Instancia
from app.services import instancia as instancias

PREFIJO_MEDIA = "/media"

UrlDeMedia = Callable[[str], str | None]

logger = logging.getLogger("validacion.contenido")


@dataclass(frozen=True)
class CasoUbicado:
    caso: Caso
    seccion_id: str
    sistema: str


@dataclass(frozen=True)
class HerramientaUbicada:
    herramienta: Herramienta
    seccion_id: str
    seccion_titulo: str
    sistema: str


@dataclass(frozen=True)
class Contenido:
    respuesta: ContenidoResponse
    casos: dict[str, CasoUbicado] = field(default_factory=dict)
    herramientas: dict[str, HerramientaUbicada] = field(default_factory=dict)
    instancia: Instancia = field(default_factory=Instancia)


_cache: dict[str, tuple[tuple, Contenido]] = {}
_candado = threading.Lock()


def _archivos(raiz: Path) -> list[Path]:
    secciones = sorted((raiz / "secciones").glob("*.yaml"))
    procedimientos = sorted(raiz.glob("procedimientos*.yaml"))
    return secciones + procedimientos


def _firma(raiz: Path) -> tuple:
    media = raiz / "media"
    nombres_media = sorted(p.name for p in media.glob("*.webp")) if media.is_dir() else []
    archivos = tuple((str(p), p.stat().st_mtime_ns) for p in _archivos(raiz))
    ruta_instancia = instancias.ruta_de(raiz)
    if ruta_instancia.is_file():
        archivos += ((str(ruta_instancia), ruta_instancia.stat().st_mtime_ns),)
    return archivos, tuple(nombres_media)


def leer_yaml(ruta: Path) -> object:
    with ruta.open(encoding="utf-8") as archivo:
        return yaml.safe_load(archivo)


def _url_media(raiz: Path, procedimiento_id: str) -> str | None:
    if (raiz / "media" / f"{procedimiento_id}.webp").is_file():
        return f"{PREFIJO_MEDIA}/{procedimiento_id}.webp"
    return None


def normalizar_procedimientos(datos: object) -> list[dict]:
    if datos is None:
        return []
    if isinstance(datos, dict) and "procedimientos" in datos:
        datos = datos["procedimientos"]
    if isinstance(datos, dict):
        return [{"id": clave, **(valor or {})} for clave, valor in datos.items()]
    if isinstance(datos, list):
        return datos
    raise ValueError("procedimientos debe ser una lista o un mapa por id")


def _seccion_de(ruta: Path) -> Seccion:
    try:
        return Seccion.model_validate(leer_yaml(ruta))
    except (ValidationError, yaml.YAMLError, OSError) as error:
        raise ValueError(f"{ruta.name}: {error}") from error


def _procedimientos_de(raiz: Path, ruta: Path) -> list[Procedimiento]:
    try:
        datos = normalizar_procedimientos(leer_yaml(ruta))
        leidos = [Procedimiento.model_validate(d) for d in datos]
    except (ValidationError, yaml.YAMLError, OSError, TypeError) as error:
        raise ValueError(f"{ruta.name}: {error}") from error
    for procedimiento in leidos:
        procedimiento.url = _url_media(raiz, procedimiento.id)
    return leidos


def registrar_seccion(
    url_de: UrlDeMedia, seccion: Seccion, casos: dict, herramientas: dict, errores: list[str]
) -> None:
    for herramienta in seccion.herramientas:
        if herramienta.id != HERRAMIENTA_GENERAL and herramienta.id not in herramientas:
            herramientas[herramienta.id] = HerramientaUbicada(
                herramienta, seccion.id, seccion.titulo, seccion.sistema
            )
    for item in seccion.media:
        item.url = url_de(item.procedimiento)
    unicos = []
    for caso in seccion.casos:
        if caso.id in casos:
            errores.append(f"{seccion.id}: el caso {caso.id} está repetido y se omitió")
            continue
        casos[caso.id] = CasoUbicado(caso=caso, seccion_id=seccion.id, sistema=seccion.sistema)
        unicos.append(caso)
    seccion.casos = unicos


@dataclass
class Armado:
    errores: list[str]
    secciones: list[Seccion] = field(default_factory=list)
    procedimientos: dict[str, Procedimiento] = field(default_factory=dict)
    casos: dict[str, CasoUbicado] = field(default_factory=dict)
    herramientas: dict[str, HerramientaUbicada] = field(default_factory=dict)

    def agregar(self, url_de: UrlDeMedia, seccion: Seccion) -> None:
        registrar_seccion(url_de, seccion, self.casos, self.herramientas, self.errores)
        self.secciones.append(seccion)

    def terminar(self, instancia: Instancia) -> Contenido:
        for error in self.errores:
            logger.warning("contenido: %s", error)
        self.secciones.sort(key=lambda s: (s.orden, s.id))
        respuesta = ContenidoResponse(
            secciones=self.secciones,
            procedimientos=list(self.procedimientos.values()),
            errores=self.errores,
        )
        return Contenido(
            respuesta=respuesta,
            casos=self.casos,
            herramientas=self.herramientas,
            instancia=instancia,
        )


def _construir(raiz: Path) -> Contenido:
    armado = Armado(errores=[])
    instancia = instancias.leer(raiz, armado.errores)
    for ruta in sorted((raiz / "secciones").glob("*.yaml")):
        try:
            seccion = _seccion_de(ruta)
        except ValueError as error:
            armado.errores.append(str(error))
            continue
        if seccion.oculta:
            continue
        if any(s.id == seccion.id for s in armado.secciones):
            armado.errores.append(f"{ruta.name}: la sección {seccion.id} está repetida y se omitió")
            continue
        armado.agregar(lambda p: _url_media(raiz, p), seccion)
    for ruta in sorted(raiz.glob("procedimientos*.yaml")):
        try:
            armado.procedimientos.update({p.id: p for p in _procedimientos_de(raiz, ruta)})
        except ValueError as error:
            armado.errores.append(str(error))
    return armado.terminar(instancia)


def _vacio() -> Contenido:
    armado = Armado(errores=[])
    return armado.terminar(instancias.leer(Path(settings.contenido_dir), armado.errores))


def cargar(raiz: Path | None = None, proyecto: Proyecto | None = None) -> Contenido:
    if raiz is None and settings.contenido_en_base:
        from app.services import contenido_base

        return contenido_base.cargar(proyecto.id if proyecto is not None else None)
    if raiz is None and proyecto is not None and not proyecto.por_omision:
        return _vacio()
    raiz = raiz or Path(settings.contenido_dir)
    clave = str(raiz)
    firma = _firma(raiz)
    with _candado:
        guardado = _cache.get(clave)
        if guardado is not None and guardado[0] == firma:
            return guardado[1]
        contenido = _construir(raiz)
        _cache[clave] = (firma, contenido)
        return contenido


def obtener(proyecto: Proyecto | None = None) -> Contenido:
    try:
        return cargar(proyecto=proyecto)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"El contenido de la validación no es válido: {error}",
        ) from None


def caso_o_404(contenido: Contenido, caso_id: str) -> CasoUbicado:
    ubicado = contenido.casos.get(caso_id)
    if ubicado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso no encontrado")
    return ubicado


def casos_de_secciones(contenido: Contenido, secciones: set[str] | None) -> list[CasoUbicado]:
    return [
        ubicado
        for ubicado in contenido.casos.values()
        if secciones is None or ubicado.seccion_id in secciones
    ]
