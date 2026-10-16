from datetime import datetime
from typing import Self

from pydantic import BaseModel, Field, field_validator, model_validator


class AvisoCreate(BaseModel):
    destinatarios: list[str] = Field(default_factory=list, max_length=50)
    titulo: str | None = Field(default=None, max_length=200)
    mensaje: str = Field(min_length=1, max_length=2000)
    falla_id: int | None = None

    @field_validator("destinatarios")
    @classmethod
    def sin_duplicados(cls, valor: list[str]) -> list[str]:
        limpios = [email.strip() for email in valor]
        if any(len(email) < 3 or len(email) > 200 for email in limpios):
            raise ValueError("Destinatario inválido")
        if len({email.lower() for email in limpios}) != len(limpios):
            raise ValueError("Hay destinatarios duplicados")
        return limpios

    @field_validator("mensaje")
    @classmethod
    def mensaje_no_vacio(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("El mensaje no puede estar vacío")
        return valor.strip()

    @model_validator(mode="after")
    def con_destino(self) -> Self:
        if not self.destinatarios and self.falla_id is None:
            raise ValueError("Indica al menos un destinatario")
        return self


class AvisoResponse(BaseModel):
    id: int
    usuario_email: str
    titulo: str
    mensaje: str
    falla_id: int | None
    caso_id: str | None
    proyecto_clave: str | None = None
    autor_email: str
    autor_nombre: str
    creado: datetime
    leido: datetime | None

    model_config = {"from_attributes": True}


class NoLeidosResponse(BaseModel):
    total: int


class PersonaAviso(BaseModel):
    email: str
    nombre: str

    model_config = {"from_attributes": True}
