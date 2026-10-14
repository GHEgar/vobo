from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

TipoAprobacion = Literal["herramienta", "caracteristica"]
EstadoAprobacion = Literal["aprobada", "rechazada", "pendiente"]


class AprobacionItem(BaseModel):
    tipo: TipoAprobacion
    objetivo_id: str = Field(min_length=1, max_length=120)
    estado: EstadoAprobacion
    comentario: str = Field(default="", max_length=2000)


class AprobacionCreate(BaseModel):
    ronda_id: int
    items: list[AprobacionItem] = Field(min_length=1, max_length=500)


class AprobacionRegistro(BaseModel):
    id: int
    estado: EstadoAprobacion
    comentario: str
    usuario_email: str
    usuario_nombre: str
    creada: datetime

    model_config = {"from_attributes": True}


class EstadoCaracteristica(BaseModel):
    caso_id: str
    estado: EstadoAprobacion
    origen: Literal["explicita", "herramienta", "ninguna"]
    actual: AprobacionRegistro | None
    historial: list[AprobacionRegistro]


class EstadoHerramienta(BaseModel):
    herramienta_id: str
    estado: Literal["aprobada", "rechazada", "pendiente", "aprobada_parcial"]
    actual: AprobacionRegistro | None
    historial: list[AprobacionRegistro]
    caracteristicas: list[EstadoCaracteristica]


class AprobacionesResponse(BaseModel):
    ronda_id: int
    herramientas: list[EstadoHerramienta]
