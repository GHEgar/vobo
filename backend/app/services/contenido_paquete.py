import io
import logging
import zipfile
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

import yaml
from fastapi import HTTPException
from pydantic import ValidationError

from app.schemas.contenido import Procedimiento, Seccion
from app.services import contenido_media as medias
from app.services.contenido import normalizar_procedimientos

MAX_ZIP = 200 * 1024 * 1024
MAX_ENTRADAS = 2000
MAX_YAML = 2 * 1024 * 1024

logger = logging.getLogger("validacion.contenido")

Lector = Callable[[], bytes]


@dataclass
class Paquete:
    secciones: list[dict] = field(default_factory=list)
    procedimientos: list[dict] = field(default_factory=list)
    media: dict[str, medias.Archivo] = field(default_factory=dict)
    errores: list[str] = field(default_factory=list)
    ignorados: list[str] = field(default_factory=list)

    @property
    def vacio(self) -> bool:
        return not (self.secciones or self.procedimientos or self.media)


def _yaml(nombre: str, leer: Lector) -> object:
    contenido = leer()
    if len(contenido) > MAX_YAML:
        raise ValueError("pesa más de 2 MB")
    return yaml.safe_load(contenido.decode("utf-8"))


def _seccion(paquete: Paquete, nombre: str, leer: Lector, estricto: bool) -> None:
    try:
        datos = _yaml(nombre, leer)
        seccion = Seccion.model_validate(datos)
    except (ValidationError, yaml.YAMLError, UnicodeDecodeError, ValueError) as error:
        paquete.errores.append(f"{nombre}: {error}")
        return
    if any(s["id"] == seccion.id for s in paquete.secciones):
        paquete.errores.append(f"{nombre}: la sección {seccion.id} está repetida y se omitió")
        return
    if estricto:
        vistos = {c["id"] for s in paquete.secciones for c in s.get("casos") or []}
        propios = [c.id for c in seccion.casos]
        repetidos = sorted({c for c in propios if c in vistos or propios.count(c) > 1})
        if repetidos:
            paquete.errores.append(f"{nombre}: casos repetidos: {', '.join(repetidos)}")
            return
    paquete.secciones.append(datos)


def _procedimientos(paquete: Paquete, nombre: str, leer: Lector) -> None:
    try:
        lista = normalizar_procedimientos(_yaml(nombre, leer))
        validos = [(d, Procedimiento.model_validate(d)) for d in lista]
    except (ValidationError, yaml.YAMLError, UnicodeDecodeError, ValueError, TypeError) as error:
        paquete.errores.append(f"{nombre}: {error}")
        return
    posiciones = {d["id"]: i for i, d in enumerate(paquete.procedimientos)}
    for datos, procedimiento in validos:
        datos = {**datos, "id": procedimiento.id}
        if procedimiento.id in posiciones:
            paquete.procedimientos[posiciones[procedimiento.id]] = datos
        else:
            posiciones[procedimiento.id] = len(paquete.procedimientos)
            paquete.procedimientos.append(datos)


def _media(paquete: Paquete, nombre: str, leer: Lector) -> None:
    coincide = medias.NOMBRE.match(PurePosixPath(nombre).name)
    if coincide is None or coincide["ext"] not in medias.EXTENSIONES:
        paquete.ignorados.append(nombre)
        return
    try:
        archivo = medias.validar(leer(), PurePosixPath(nombre).name)
    except HTTPException as error:
        paquete.errores.append(f"{nombre}: {error.detail}")
        return
    clave = coincide["id"]
    previo = paquete.media.get(clave)
    rango = medias.PREFERENCIA.index
    if previo is None or rango(archivo.extension) < rango(previo.extension):
        paquete.media[clave] = archivo


def leer_entradas(entradas: dict[str, Lector], estricto: bool) -> Paquete:
    paquete = Paquete()
    for nombre in sorted(entradas):
        ruta = PurePosixPath(nombre)
        leer = entradas[nombre]
        if len(ruta.parts) == 2 and ruta.parts[0] == "secciones" and ruta.suffix == ".yaml":
            _seccion(paquete, nombre, leer, estricto)
        elif len(ruta.parts) == 1 and ruta.match("procedimientos*.yaml"):
            _procedimientos(paquete, nombre, leer)
        elif len(ruta.parts) == 2 and ruta.parts[0] == "media":
            _media(paquete, nombre, leer)
        elif nombre != "instancia.yaml":
            paquete.ignorados.append(nombre)
    return paquete


def de_directorio(raiz: Path) -> Paquete:
    entradas: dict[str, Lector] = {}
    for ruta in [*raiz.glob("secciones/*.yaml"), *raiz.glob("procedimientos*.yaml")]:
        entradas[ruta.relative_to(raiz).as_posix()] = ruta.read_bytes
    for ruta in raiz.glob("media/*"):
        if ruta.is_file():
            entradas[ruta.relative_to(raiz).as_posix()] = ruta.read_bytes
    return leer_entradas(entradas, estricto=False)


def _sin_raiz_comun(nombres: list[str]) -> dict[str, str]:
    partes = [PurePosixPath(n).parts for n in nombres]
    directas = any(p[0] in {"secciones", "media"} or len(p) == 1 for p in partes)
    primeras = {p[0] for p in partes}
    if directas or len(primeras) != 1:
        return {n: n for n in nombres}
    return {PurePosixPath(*PurePosixPath(n).parts[1:]).as_posix(): n for n in nombres}


def de_zip(contenido: bytes) -> Paquete:
    try:
        archivo = zipfile.ZipFile(io.BytesIO(contenido))
    except zipfile.BadZipFile:
        return Paquete(errores=["El archivo no es un .zip válido"])
    miembros = [i for i in archivo.infolist() if not i.is_dir()]
    if len(miembros) > MAX_ENTRADAS:
        return Paquete(errores=[f"El .zip tiene más de {MAX_ENTRADAS} archivos"])
    if sum(i.file_size for i in miembros) > MAX_ZIP:
        return Paquete(errores=["El contenido del .zip descomprimido pesa más de 200 MB"])
    seguros = [
        i.filename
        for i in miembros
        if not i.filename.startswith("/")
        and ".." not in PurePosixPath(i.filename).parts
        and PurePosixPath(i.filename).parts[0] != "__MACOSX"
    ]
    nombres = _sin_raiz_comun([n for n in seguros if not PurePosixPath(n).name.startswith(".")])
    entradas = {
        limpio: (lambda n=original: archivo.read(n)) for limpio, original in nombres.items()
    }
    return leer_entradas(entradas, estricto=True)
