from pydantic import BaseModel, Field

from app.schemas.herramienta import DecisionResponse


class Celda(BaseModel):
    familia: str
    total: int
    hechos: int
    pasa: int
    falla: int
    no_pude: int


class CeldaProyecto(BaseModel):
    hechos: int
    total: int
    falla: int
    asignado: bool


class FilaPersona(BaseModel):
    email: str
    nombre: str
    celdas: list[Celda]


class ConteoSeveridad(BaseModel):
    severidad: str
    abiertas: int
    total: int


class Criterio(BaseModel):
    clave: str
    descripcion: str
    cumple: bool
    detalle: str


class TableroResponse(BaseModel):
    ronda_id: int
    familias: list[str]
    personas: list[FilaPersona]
    fallas: list[ConteoSeveridad]
    casos_total: int
    casos_ejecutados: int
    criterios: list[Criterio]
    veredicto: str
    razones: list[str]
    decisiones: list[DecisionResponse]
    proyectos: list[str] = Field(default_factory=list)
    por_proyecto: dict[str, dict[str, CeldaProyecto]] = Field(default_factory=dict)
    cobertura: dict[str, int] = Field(default_factory=dict)
