import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.instancia import (
    COLOR_HEX,
    CuentaDeInstancia,
    EntradaDeInstancia,
    InstanciaResponse,
    Sistema,
)

TOKENS = (
    "primario",
    "primario-hover",
    "primario-suave",
    "primario-claro",
    "primario-borde",
    "texto",
    "texto-tenue",
    "fondo-pagina",
    "aviso",
    "error",
    "exito",
    "nombre",
)
FUENTES = ("tema", "producto", "sistema")
RANURAS = ("logo_claro", "logo_oscuro", "favicon")
CAMPOS = (
    "producto",
    "nombre",
    "descripcion",
    "entrada",
    "logo_alt",
    "color_tema",
    "colores",
    "fuente",
    "proyectos",
    "cuentas",
)
CLAVE_PROYECTO = re.compile(r"^[a-z0-9][a-z0-9_-]{0,59}$")

Fuente = Literal["tema", "producto", "sistema"]
Ranura = Literal["logo_claro", "logo_oscuro", "favicon"]


def _color(valor: str) -> str:
    if not COLOR_HEX.match(valor):
        raise ValueError("debe tener el formato #RRGGBB")
    return valor.upper()


def _texto(valor: str, largo: int) -> str:
    limpio = valor.strip()
    if len(limpio) > largo:
        raise ValueError(f"no puede pasar de {largo} caracteres")
    return limpio


def _unicas(claves: list[str], nombre: str) -> None:
    repetidas = sorted({c for c in claves if claves.count(c) > 1})
    if repetidas:
        raise ValueError(f"{nombre} repetidos: {', '.join(repetidas)}")


class ConfiguracionCambios(BaseModel):
    model_config = ConfigDict(extra="forbid")

    producto: str = ""
    nombre: str = ""
    descripcion: str = ""
    entrada: EntradaDeInstancia = Field(default_factory=EntradaDeInstancia)
    logo_alt: str = ""
    color_tema: str = ""
    colores: dict[str, str] = Field(default_factory=dict)
    fuente: Fuente = "tema"
    proyectos: list[Sistema] = Field(default_factory=list)
    cuentas: list[CuentaDeInstancia] = Field(default_factory=list)

    @field_validator("producto")
    @classmethod
    def validar_producto(cls, valor: str) -> str:
        limpio = _texto(valor, 80)
        if not limpio:
            raise ValueError("no puede quedar vacío; usa Restablecer para volver al valor base")
        return limpio

    @field_validator("nombre", "logo_alt")
    @classmethod
    def validar_corto(cls, valor: str) -> str:
        return _texto(valor, 120)

    @field_validator("descripcion")
    @classmethod
    def validar_descripcion(cls, valor: str) -> str:
        return _texto(valor, 500)

    @field_validator("entrada")
    @classmethod
    def validar_entrada(cls, valor: EntradaDeInstancia) -> EntradaDeInstancia:
        return EntradaDeInstancia(
            titulo=_texto(valor.titulo, 120), mensaje=_texto(valor.mensaje, 1000)
        )

    @field_validator("color_tema")
    @classmethod
    def validar_color_tema(cls, valor: str) -> str:
        return _color(valor)

    @field_validator("colores")
    @classmethod
    def validar_colores(cls, valor: dict[str, str]) -> dict[str, str]:
        ajenos = sorted(set(valor) - set(TOKENS))
        if ajenos:
            raise ValueError(f"colores no editables: {', '.join(ajenos)}")
        return {t: _color(valor[t]) for t in TOKENS if t in valor}

    @field_validator("proyectos")
    @classmethod
    def validar_proyectos(cls, valor: list[Sistema]) -> list[Sistema]:
        limpios = [Sistema(clave=p.clave.strip(), nombre=_texto(p.nombre, 120)) for p in valor]
        for proyecto in limpios:
            if not CLAVE_PROYECTO.match(proyecto.clave):
                raise ValueError(
                    f"la clave «{proyecto.clave}» debe ir en minúsculas, números, - o _"
                )
            if not proyecto.nombre:
                raise ValueError(f"el proyecto {proyecto.clave} necesita nombre")
        _unicas([p.clave for p in limpios], "proyectos")
        return limpios

    @field_validator("cuentas")
    @classmethod
    def validar_cuentas(cls, valor: list[CuentaDeInstancia]) -> list[CuentaDeInstancia]:
        limpias = [
            CuentaDeInstancia(prefijo=c.prefijo.strip(), descripcion=_texto(c.descripcion, 200))
            for c in valor
        ]
        if any(not c.prefijo or not c.descripcion for c in limpias):
            raise ValueError("cada cuenta necesita prefijo y descripción")
        _unicas([c.prefijo.lower() for c in limpias], "prefijos")
        return limpias


class ArchivoDeMarca(BaseModel):
    archivo: str
    mime: str
    tamano: int
    huella: str
    url: str


class ConfiguracionResponse(BaseModel):
    guardada: dict[str, object]
    archivos: dict[str, object]
    marca: dict[str, ArchivoDeMarca]
    efectiva: InstanciaResponse
    colores: dict[str, str]
    fuente: str
    tokens: list[str]
    fuentes: list[str]
    proyectos_en_uso: list[str]
