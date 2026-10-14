from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

EstadoResultado = Literal["pendiente", "pasa", "falla", "no_pude"]
EstadoPaso = Literal["pasa", "falla", "comentario", "no_pude"]


class PasoMarcado(BaseModel):
    paso: int = Field(ge=0)
    estado: EstadoPaso
    comentario: str | None = Field(default=None, max_length=1000)


def normalizar_pasos(valor: object) -> object:
    if not isinstance(valor, list):
        return valor
    return [{"paso": p, "estado": "pasa"} if isinstance(p, int) else p for p in valor]


class ResultadoUpdate(BaseModel):
    ronda_id: int
    estado: EstadoResultado
    pasos_marcados: list[PasoMarcado] = Field(default_factory=list, max_length=100)
    comentario: str | None = Field(default=None, max_length=1000)

    _legado = field_validator("pasos_marcados", mode="before")(normalizar_pasos)


class ResultadoResponse(BaseModel):
    caso_id: str
    estado: EstadoResultado
    pasos_marcados: list[PasoMarcado]
    comentario: str | None = None
    actualizado: datetime

    model_config = {"from_attributes": True}

    _legado = field_validator("pasos_marcados", mode="before")(normalizar_pasos)


class MisCasosResponse(BaseModel):
    ronda_id: int
    secciones_asignadas: list[str]
    secciones_visibles: list[str] = Field(default_factory=list)
    ve_tecnico: bool = False
    resultados: list[ResultadoResponse]


class ComentarioResponse(BaseModel):
    ronda_id: int
    caso_id: str
    caso_titulo: str
    sistema: str
    usuario_email: str
    autor: str = ""
    ronda_nombre: str = ""
    paso: int | None
    paso_texto: str
    tipo: Literal["paso", "no_pude"]
    comentario: str
    actualizado: datetime
