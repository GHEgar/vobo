from typing import Literal

from pydantic import BaseModel

TipoResultado = Literal["seccion", "caso", "paso", "herramienta", "procedimiento"]


class ResultadoBusqueda(BaseModel):
    tipo: TipoResultado
    id: str
    titulo: str
    contexto: str
    ruta: str
