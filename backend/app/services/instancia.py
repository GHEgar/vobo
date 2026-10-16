from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from app.schemas.instancia import (
    FAVICON_POR_OMISION,
    EntradaResponse,
    Instancia,
    InstanciaResponse,
    LogoResponse,
    url_de_tema,
)

ARCHIVO = "instancia.yaml"


def ruta_de(raiz: Path) -> Path:
    return raiz / ARCHIVO


def _validar(datos: dict[str, Any], errores: list[str]) -> Instancia:
    try:
        return Instancia.model_validate(datos)
    except ValidationError as error:
        errores.append(f"{ARCHIVO}: {error}")
        invalidos = {e["loc"][0] for e in error.errors() if e["loc"]}
        restantes = {k: v for k, v in datos.items() if k not in invalidos}
        if not invalidos or restantes == datos:
            return Instancia()
        try:
            return Instancia.model_validate(restantes)
        except ValidationError:
            return Instancia()


def leer(raiz: Path, errores: list[str]) -> Instancia:
    ruta = ruta_de(raiz)
    if not ruta.is_file():
        return Instancia()
    try:
        with ruta.open(encoding="utf-8") as archivo:
            datos = yaml.safe_load(archivo)
        if datos is None:
            return Instancia()
        if not isinstance(datos, dict):
            raise ValueError("debe ser un mapa de campos")
    except (yaml.YAMLError, OSError, ValueError) as error:
        errores.append(f"{ARCHIVO}: {error}")
        return Instancia()
    limpios = {k: v for k, v in datos.items() if v is not None}
    if "sistemas" in limpios:
        limpios["proyectos"] = limpios.pop("sistemas")
    return _validar(limpios, errores)


def _logo(instancia: Instancia) -> LogoResponse | None:
    if instancia.logo is None:
        return None
    claro = url_de_tema(instancia.logo.claro)
    oscuro = url_de_tema(instancia.logo.oscuro) if instancia.logo.oscuro else claro
    return LogoResponse(claro=claro, oscuro=oscuro, alt=instancia.logo.alt or instancia.producto)


def respuesta(instancia: Instancia) -> InstanciaResponse:
    return InstanciaResponse(
        producto=instancia.producto,
        nombre=instancia.nombre,
        descripcion=instancia.descripcion,
        logo=_logo(instancia),
        favicon=url_de_tema(instancia.favicon) if instancia.favicon else FAVICON_POR_OMISION,
        color_tema=instancia.color_tema,
        entrada=EntradaResponse(titulo=instancia.entrada.titulo, mensaje=instancia.entrada.mensaje),
        proyectos=instancia.proyectos,
        sistemas=instancia.proyectos,
    )
