from datetime import datetime
from typing import Literal

from pydantic import BaseModel

TipoEvento = Literal[
    "resultado", "falla", "comentario", "aprobacion", "decision", "aviso", "sesion", "contenido"
]
TIPOS_EVENTO: tuple[str, ...] = TipoEvento.__args__


class UsuarioEvento(BaseModel):
    email: str
    nombre: str


class EventoActividad(BaseModel):
    id: str
    tipo: TipoEvento
    cuando: datetime
    usuario: UsuarioEvento
    resumen: str
    caso_id: str | None = None
    caso_titulo: str | None = None
    seccion_id: str | None = None
    paso: int | None = None
    ronda_id: int | None = None
    ruta: str | None = None
    estado: str | None = None
    comentario: str | None = None
    severidad: str | None = None
    capturas: int | None = None
    aproximado: bool = False


class PaginaActividad(BaseModel):
    eventos: list[EventoActividad]
    siguiente: str | None
