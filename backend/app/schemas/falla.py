from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.seguimiento import EventoSeguimiento

EstadoFalla = Literal["nueva", "en_curso", "lista_para_revalidar", "cerrada"]
Reproducible = Literal["siempre", "a_veces", "una_vez"]
TipoFalla = Literal["falla", "no_pude"]


class EvidenciaResponse(BaseModel):
    id: int
    mime: str
    url: str


class FallaResponse(BaseModel):
    id: int
    ronda_id: int
    caso_id: str
    caso_titulo: str
    seccion_id: str
    seccion_titulo: str = ""
    seccion_completa: bool = False
    tipo: TipoFalla = "falla"
    sistema: str
    familia: str
    usuario_email: str
    paso: int | None
    paso_texto: str
    obtenido: str
    reproducible: Reproducible
    severidad: str
    navegador: str
    url: str
    version_visible: str
    creada: datetime
    estado: EstadoFalla
    nota_resolucion: str
    evidencias: list[EvidenciaResponse]
    plazo: date | None = None
    plazo_por: str | None = None
    plazo_por_nombre: str = ""
    resuelta_en: datetime | None = None
    resuelta_por: str | None = None
    resuelta_por_nombre: str = ""
    seguimiento: list[EventoSeguimiento] = Field(default_factory=list)


class FallaUpdate(BaseModel):
    estado: EstadoFalla | None = None
    nota_resolucion: str | None = Field(default=None, max_length=4000)
    plazo: date | None = None
