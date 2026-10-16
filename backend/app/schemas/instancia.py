import re
from pathlib import PurePosixPath
from urllib.parse import quote

from pydantic import BaseModel, Field, field_validator

PRODUCTO_POR_OMISION = "VoBo"
FAVICON_POR_OMISION = "/favicon.svg"
COLOR_TEMA_POR_OMISION = "#1F4E79"
PREFIJO_TEMA = "/tema/"
COLOR_HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
ESQUEMA = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
PROHIBIDOS = ("\\", "?", "#")


def ruta_de_tema(valor: str) -> str:
    texto = valor.strip()
    if not texto:
        raise ValueError("la ruta está vacía")
    if texto.startswith("/") or ESQUEMA.match(texto) or any(c in texto for c in PROHIBIDOS):
        raise ValueError("debe ser una ruta relativa a la carpeta del tema")
    partes = [p for p in PurePosixPath(texto).parts if p != "."]
    if not partes or ".." in partes:
        raise ValueError("no puede salir de la carpeta del tema")
    return "/".join(partes)


def url_de_tema(ruta: str) -> str:
    return PREFIJO_TEMA + quote(ruta)


class Sistema(BaseModel):
    clave: str
    nombre: str


class CuentaDeInstancia(BaseModel):
    prefijo: str
    descripcion: str


class LogoDeInstancia(BaseModel):
    claro: str
    oscuro: str | None = None
    alt: str = ""

    @field_validator("claro", "oscuro")
    @classmethod
    def validar_ruta(cls, valor: str | None) -> str | None:
        return None if valor is None else ruta_de_tema(valor)


class EntradaDeInstancia(BaseModel):
    titulo: str = ""
    mensaje: str = ""


class Instancia(BaseModel):
    producto: str = PRODUCTO_POR_OMISION
    nombre: str = ""
    descripcion: str = ""
    logo: LogoDeInstancia | None = None
    favicon: str | None = None
    color_tema: str = COLOR_TEMA_POR_OMISION
    color_nombre: str | None = None
    entrada: EntradaDeInstancia = Field(default_factory=EntradaDeInstancia)
    proyectos: list[Sistema] = Field(default_factory=list)
    cuentas: list[CuentaDeInstancia] = Field(default_factory=list)

    @field_validator("producto")
    @classmethod
    def validar_producto(cls, valor: str) -> str:
        return valor.strip() or PRODUCTO_POR_OMISION

    @field_validator("favicon")
    @classmethod
    def validar_favicon(cls, valor: str | None) -> str | None:
        return None if valor is None else ruta_de_tema(valor)

    @field_validator("color_tema", "color_nombre")
    @classmethod
    def validar_color(cls, valor: str | None) -> str | None:
        if valor is None:
            return None
        if not COLOR_HEX.match(valor):
            raise ValueError("debe tener el formato #RRGGBB")
        return valor.upper()


class LogoResponse(BaseModel):
    claro: str
    oscuro: str
    alt: str


class EntradaResponse(BaseModel):
    titulo: str
    mensaje: str


class ProyectoPublico(BaseModel):
    clave: str
    nombre: str
    color_nombre: str | None = None
    por_omision: bool = False


class InstanciaResponse(BaseModel):
    producto: str
    nombre: str
    descripcion: str
    logo: LogoResponse | None
    favicon: str
    color_tema: str
    entrada: EntradaResponse
    proyectos: list[Sistema]
    sistemas: list[Sistema] = Field(default_factory=list)
    proyecto: ProyectoPublico | None = None


class VersionResponse(BaseModel):
    version: str
