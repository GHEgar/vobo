from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.instancia import ProyectoPublico, Sistema


class EstadoEditor(BaseModel):
    fuente: Literal["archivos", "base"]
    editable: bool
    proyectos: list[Sistema]
    sistemas: list[Sistema]
    proyecto: ProyectoPublico
    errores: list[str]


class Documento(BaseModel):
    datos: dict[str, Any]


class Duplicado(BaseModel):
    id: str = Field(min_length=1, max_length=120)


class Orden(BaseModel):
    ids: list[str]


class Oculta(BaseModel):
    oculta: bool


class SeccionResumen(BaseModel):
    id: str
    orden: int
    titulo: str
    sistema: str
    audiencia: str
    oculta: bool
    casos: int
    con_resultados: bool
    actualizado: datetime
    autor_email: str


class SeccionDetalle(BaseModel):
    id: str
    datos: dict[str, Any]
    actualizado: datetime
    autor_email: str
    con_resultados: bool
    casos_bloqueados: list[str]
    herramientas_bloqueadas: list[str]


class MediaInfo(BaseModel):
    archivo: str
    mime: str
    tamano: int
    url: str
    subido: datetime
    autor_email: str


class ProcedimientoDetalle(BaseModel):
    id: str
    datos: dict[str, Any]
    actualizado: datetime
    autor_email: str
    media: MediaInfo | None
    usos: list[str]


class VersionItem(BaseModel):
    id: int
    tipo: str
    objeto_id: str
    accion: str
    datos: dict[str, Any] | None
    autor_email: str
    creado: datetime


class Cambios(BaseModel):
    crear: list[str]
    actualizar: list[str]
    borrar: list[str]


class ResumenImportacion(BaseModel):
    aplicado: bool
    sin_cambios: bool
    secciones: Cambios
    procedimientos: Cambios
    media: Cambios
    bloqueos: list[str]
    ignorados: list[str]
