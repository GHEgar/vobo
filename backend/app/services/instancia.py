from pathlib import Path

import yaml
from pydantic import ValidationError

from app.schemas.instancia import Instancia, InstanciaResponse

ARCHIVO = "instancia.yaml"


def ruta_de(raiz: Path) -> Path:
    return raiz / ARCHIVO


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
        return Instancia.model_validate({k: v for k, v in datos.items() if v is not None})
    except (ValidationError, yaml.YAMLError, OSError, ValueError) as error:
        errores.append(f"{ARCHIVO}: {error}")
        return Instancia()


def respuesta(instancia: Instancia) -> InstanciaResponse:
    return InstanciaResponse(
        nombre=instancia.nombre,
        descripcion=instancia.descripcion,
        proyectos=instancia.proyectos,
    )
