from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

EstadoComentario = Literal["nuevo", "en_curso", "resuelto"]
AccionSeguimiento = Literal["respuesta", "estado", "plazo", "nota", "esfuerzo", "vinculo"]
ObjetoSeguimiento = Literal["falla", "comentario"]
ESFUERZO_MAXIMO = 1000


class EventoSeguimiento(BaseModel):
    id: int
    accion: AccionSeguimiento
    autor_email: str
    autor: str = ""
    texto: str = ""
    anterior: str | None = None
    nuevo: str | None = None
    creado: datetime


class RespuestaCreate(BaseModel):
    texto: str = Field(min_length=1, max_length=4000)

    @field_validator("texto")
    @classmethod
    def _con_texto(cls, valor: str) -> str:
        limpio = valor.strip()
        if not limpio:
            raise ValueError("La respuesta no puede estar vacía")
        return limpio


class PrincipalRef(BaseModel):
    objeto: ObjetoSeguimiento
    id: int


class PrincipalResponse(PrincipalRef):
    etiqueta: str = ""


class ComentarioUpdate(BaseModel):
    estado: EstadoComentario | None = None
    plazo: date | None = None
    esfuerzo_horas: float | None = Field(default=None, ge=0, le=ESFUERZO_MAXIMO)
    principal: PrincipalRef | None = None
