from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Familia = Literal["A", "B", "C", "D", "E", "T"]
Audiencia = Literal["funcional", "tecnica"]
Modo = Literal["prod", "beta", "dev"]
Severidad = Literal["critica", "alta", "media", "baja"]
Hoy = Literal["prod", "beta", "oculto"]

HERRAMIENTA_GENERAL = "general"


class Paso(BaseModel):
    texto: str
    procedimiento: str | None = None


class Media(BaseModel):
    procedimiento: str
    pie: str = ""
    url: str | None = None


class Herramienta(BaseModel):
    id: str
    nombre: str = ""
    hoy: Hoy = "prod"


class Caso(BaseModel):
    id: str
    familia: Familia
    herramienta: str = HERRAMIENTA_GENERAL
    titulo: str
    rol: str = ""
    cuenta: str = ""
    modo: Modo = "prod"
    antes: str = ""
    pasos: list[Paso] = Field(min_length=1)
    esperado: str
    severidad: Severidad


class Seccion(BaseModel):
    id: str
    orden: int = 0
    titulo: str
    sistema: str
    audiencia: Audiencia = "funcional"
    resumen: str = ""
    que_cambia: list[str] = Field(default_factory=list)
    donde: str = ""
    herramientas: list[Herramienta] = Field(
        default_factory=lambda: [Herramienta(id=HERRAMIENTA_GENERAL, nombre="General")]
    )
    media: list[Media] = Field(default_factory=list)
    casos: list[Caso] = Field(default_factory=list)


class Procedimiento(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    titulo: str = ""
    descripcion: str = ""
    url: str | None = None


class ContenidoResponse(BaseModel):
    secciones: list[Seccion]
    procedimientos: list[Procedimiento]
    errores: list[str] = Field(default_factory=list)
