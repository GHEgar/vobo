from typing import Literal

from pydantic import BaseModel, Field

Tono = Literal["good", "warning", "serious", "critical", "neutral"]


class Detalle(BaseModel):
    label: str
    value: str | int | float


class Estado(BaseModel):
    key: str
    label: str
    tone: Tono


class ProyectoGrafo(BaseModel):
    id: str
    name: str
    description: str | None = None
    color: str | None = None
    progress: float = Field(ge=0, le=1)
    counts: dict[str, int]
    details: list[Detalle] = []


class PersonaGrafo(BaseModel):
    id: str
    name: str
    metric: int
    active: bool
    details: list[Detalle] = []


class EnlaceGrafo(BaseModel):
    person: str
    project: str
    weight: int = Field(gt=0)


class Participacion(BaseModel):
    statuses: list[Estado]
    projects: list[ProyectoGrafo]
    people: list[PersonaGrafo]
    links: list[EnlaceGrafo]
