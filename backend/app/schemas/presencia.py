from typing import Literal

from pydantic import BaseModel, Field

AccionPresencia = Literal["viendo", "reportando", "comentando"]
EstadoPresencia = Literal["activo", "inactivo"]


class PresenciaCreate(BaseModel):
    ruta: str = Field(min_length=1, max_length=300)
    caso_id: str | None = Field(default=None, max_length=60)
    paso: int | None = Field(default=None, ge=1, le=500)
    seccion_id: str | None = Field(default=None, max_length=120)
    accion: AccionPresencia = "viendo"
    ronda_id: int | None = Field(default=None, ge=1)
    proyecto: str | None = Field(default=None, max_length=60)


class PresenciaResponse(BaseModel):
    email: str
    nombre: str
    ruta: str
    caso_id: str | None
    caso_titulo: str
    paso: int | None
    pasos_total: int | None
    seccion_id: str | None
    seccion_titulo: str
    accion: str
    ronda_id: int | None
    estado: EstadoPresencia
    hace_segundos: int
    yo: bool
