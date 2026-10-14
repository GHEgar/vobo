from typing import Literal

from pydantic import BaseModel, Field

PaginaOtorgable = Literal["tablero", "fallas", "herramientas", "tecnico"]


class AccesoItem(BaseModel):
    usuario_email: str = Field(min_length=3, max_length=200)
    paginas: list[PaginaOtorgable] = Field(default_factory=list)

    model_config = {"from_attributes": True}
