from pydantic import BaseModel, Field

NOMBRE_POR_OMISION = "Validaciones"


class Proyecto(BaseModel):
    clave: str
    nombre: str


class CuentaDeInstancia(BaseModel):
    prefijo: str
    descripcion: str


class Instancia(BaseModel):
    nombre: str = NOMBRE_POR_OMISION
    descripcion: str = ""
    proyectos: list[Proyecto] = Field(default_factory=list)
    cuentas: list[CuentaDeInstancia] = Field(default_factory=list)


class InstanciaResponse(BaseModel):
    nombre: str
    descripcion: str
    proyectos: list[Proyecto]
