from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

DecisionValor = Literal["desplegar", "desplegar_con_aviso", "aplazar", "pendiente"]
Sugerencia = Literal["desplegar", "desplegar_con_aviso", "aplazar", "sin_probar"]


class DecisionUpdate(BaseModel):
    ronda_id: int
    decision: DecisionValor
    motivo: str = Field(default="", max_length=2000)


class DecisionResponse(BaseModel):
    herramienta_id: str
    decision: DecisionValor
    motivo: str
    decidido_por: str
    actualizado: datetime

    model_config = {"from_attributes": True}


class Caracteristica(BaseModel):
    caso_id: str
    titulo: str
    estado: str
    fallas_abiertas: int


class HerramientaResumen(BaseModel):
    id: str
    nombre: str
    hoy: str
    seccion_id: str
    seccion_titulo: str
    audiencia: str = "funcional"
    sistema: str
    casos_total: int
    casos: dict[str, int]
    fallas_abiertas: dict[str, int]
    sugerencia: Sugerencia
    sugerencia_motivo: str
    decision: DecisionResponse | None
    caracteristicas: list[Caracteristica] = Field(default_factory=list)
