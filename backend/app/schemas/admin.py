import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

PATRON_CORREO = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


def correo_normalizado(valor: str) -> str:
    return valor.strip().lower()


class PermisoItem(BaseModel):
    clave: str
    descripcion: str


class RolItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    clave: str
    nombre: str
    descripcion: str
    permisos: list[str]
    sistema: bool


class RolCrear(BaseModel):
    clave: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{1,59}$")
    nombre: str = Field(min_length=1, max_length=120)
    descripcion: str = Field(default="", max_length=500)
    permisos: list[str] = Field(default_factory=list)


class RolCambios(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=120)
    descripcion: str | None = Field(default=None, max_length=500)
    permisos: list[str] | None = None


class CuentaResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    activa: bool
    creada: datetime
    ultimo_cambio: datetime


class PersonaItem(BaseModel):
    id: int
    email: str
    nombre: str
    ultimo_acceso: datetime
    oidc: bool
    roles: list[str]
    cuenta: CuentaResumen | None


class RolesDePersona(BaseModel):
    roles: list[str]


class EstadoCuenta(BaseModel):
    activa: bool


class InvitacionCrear(BaseModel):
    email: str = Field(max_length=200)
    roles: list[str] = Field(default_factory=list)

    @field_validator("email")
    @classmethod
    def con_formato(cls, valor: str) -> str:
        correo = correo_normalizado(valor)
        if not re.match(PATRON_CORREO, correo):
            raise ValueError("Correo no válido")
        return correo


class InvitacionItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    roles: list[str]
    creada_por: str
    creada: datetime
    expira: datetime


class EnlaceResponse(BaseModel):
    enlace: str
    expira: datetime
