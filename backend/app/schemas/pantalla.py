from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Vista = Literal["general", "grafo"]


def _vistas(valor: list[str] | None) -> list[str] | None:
    if valor is None:
        return None
    unicas = list(dict.fromkeys(valor))
    if not unicas:
        raise ValueError("Elige al menos una vista")
    return unicas


def _proyectos(valor: list[str] | None) -> list[str] | None:
    return None if valor is None else list(dict.fromkeys(valor))


def _nombre(valor: str | None) -> str | None:
    if valor is None:
        return None
    if not valor.strip():
        raise ValueError("El nombre no puede estar vacío")
    return valor.strip()


class PantallaCrear(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    vistas: list[Vista] = Field(default_factory=lambda: ["general", "grafo"], max_length=2)
    segundos: int = Field(default=20, ge=10, le=300)
    proyectos: list[str] = Field(default_factory=list, max_length=50)

    @field_validator("nombre")
    @classmethod
    def nombre_limpio(cls, valor: str | None) -> str | None:
        return _nombre(valor)

    @field_validator("vistas")
    @classmethod
    def vistas_unicas(cls, valor: list[str] | None) -> list[str] | None:
        return _vistas(valor)

    @field_validator("proyectos")
    @classmethod
    def proyectos_unicos(cls, valor: list[str] | None) -> list[str] | None:
        return _proyectos(valor)


class PantallaCambios(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=120)
    vistas: list[Vista] | None = Field(default=None, max_length=2)
    segundos: int | None = Field(default=None, ge=10, le=300)
    proyectos: list[str] | None = Field(default=None, max_length=50)
    activa: bool | None = None

    @field_validator("nombre")
    @classmethod
    def nombre_limpio(cls, valor: str | None) -> str | None:
        return _nombre(valor)

    @field_validator("vistas")
    @classmethod
    def vistas_unicas(cls, valor: list[str] | None) -> list[str] | None:
        return _vistas(valor)

    @field_validator("proyectos")
    @classmethod
    def proyectos_unicos(cls, valor: list[str] | None) -> list[str] | None:
        return _proyectos(valor)


class PantallaItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    vistas: list[str]
    segundos: int
    proyectos: list[str]
    activa: bool
    creada: datetime
    ultimo_uso: datetime | None
    autor_email: str


class PantallaEnlace(BaseModel):
    pantalla: PantallaItem
    enlace: str


class MarcaPantalla(BaseModel):
    producto: str
    nombre: str
    logo: str | None
    color_tema: str


class PantallaPublica(BaseModel):
    nombre: str
    vistas: list[str]
    segundos: int
    marca: MarcaPantalla


class Conteos(BaseModel):
    pasa: int = 0
    falla: int = 0
    no_pude: int = 0
    pendiente: int = 0


class RondaPantalla(BaseModel):
    nombre: str
    dia: int


class CasoGrafo(BaseModel):
    id: str
    estado: str


class SeccionGrafo(BaseModel):
    id: str
    titulo: str
    avance: float
    conteos: Conteos
    casos: list[CasoGrafo] | None = None


class SistemaGrafo(BaseModel):
    nombre: str
    secciones: list[SeccionGrafo]


class ProyectoPantalla(BaseModel):
    clave: str
    nombre: str
    color: str
    logo: str | None = None
    ronda: RondaPantalla | None
    conteos: Conteos
    total: int
    avance: float
    fallas_abiertas: int
    en_linea: int
    agrupado: bool
    sistemas: list[SistemaGrafo]


class ActualPersona(BaseModel):
    proyecto: str
    caso_id: str | None = None
    seccion_id: str | None = None


class PersonaPantalla(BaseModel):
    id: str
    nombre: str
    iniciales: str
    color: str
    activa: bool
    participa: dict[str, int]
    marcados: int
    asignados: int
    avance: float
    actual: ActualPersona | None = None


class EventoPantalla(BaseModel):
    id: str
    quien: str
    color: str
    proyecto: str
    texto: str
    cuando: datetime


class DatosPantalla(BaseModel):
    generado: datetime
    proyectos: list[ProyectoPantalla]
    personas: list[PersonaPantalla]
    eventos: list[EventoPantalla]
