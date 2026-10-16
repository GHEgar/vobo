from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class RondaCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    snapshot: str = Field(default="", max_length=200)
    proyecto: str | None = Field(default=None, max_length=60)


class RondaUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=120)
    snapshot: str | None = Field(default=None, max_length=200)
    abierta: bool | None = None


class RondaResponse(BaseModel):
    id: int
    proyecto_id: int
    nombre: str
    snapshot: str
    abierta: bool
    creada: datetime

    model_config = {"from_attributes": True}


class AsignacionItem(BaseModel):
    usuario_email: str = Field(min_length=3, max_length=200)
    seccion_id: str = Field(min_length=1, max_length=120)


class AsignacionResponse(AsignacionItem):
    id: int

    model_config = {"from_attributes": True}


class UsuarioConocido(BaseModel):
    email: str
    nombre: str
    permisos: list[str] = Field(default_factory=list)

    @field_validator("permisos", mode="before")
    @classmethod
    def sin_nulos(cls, valor: object) -> object:
        return valor or []

    model_config = {"from_attributes": True}
