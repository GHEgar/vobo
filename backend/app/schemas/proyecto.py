from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.instancia import COLOR_HEX

PATRON_CLAVE = r"^[a-z0-9][a-z0-9-]{0,59}$"


def _color(valor: str | None) -> str | None:
    if valor is None or not valor.strip():
        return None
    if not COLOR_HEX.match(valor.strip()):
        raise ValueError("debe tener el formato #RRGGBB")
    return valor.strip().upper()


class ProyectoItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    clave: str
    nombre: str
    descripcion: str
    color_nombre: str | None
    orden: int
    archivado: bool
    por_omision: bool


class ProyectoAdmin(ProyectoItem):
    rondas: int = 0
    secciones: int = 0


class ProyectosAdmin(BaseModel):
    fuente: str
    multiples: bool
    motivo: str
    proyectos: list[ProyectoAdmin]


class ProyectoCrear(BaseModel):
    clave: str = Field(pattern=PATRON_CLAVE)
    nombre: str = Field(min_length=1, max_length=120)
    descripcion: str = Field(default="", max_length=1000)
    color_nombre: str | None = None

    @field_validator("nombre")
    @classmethod
    def nombre_limpio(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("El nombre no puede estar vacío")
        return valor.strip()

    @field_validator("color_nombre")
    @classmethod
    def validar_color(cls, valor: str | None) -> str | None:
        return _color(valor)


class ProyectoCambios(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=120)
    descripcion: str | None = Field(default=None, max_length=1000)
    color_nombre: str | None = None
    archivado: bool | None = None
    por_omision: bool | None = None

    @field_validator("nombre")
    @classmethod
    def nombre_limpio(cls, valor: str | None) -> str | None:
        if valor is not None and not valor.strip():
            raise ValueError("El nombre no puede estar vacío")
        return valor.strip() if valor is not None else None

    @field_validator("color_nombre")
    @classmethod
    def validar_color(cls, valor: str | None) -> str | None:
        return _color(valor)


class OrdenProyectos(BaseModel):
    ids: list[int] = Field(min_length=1, max_length=500)
