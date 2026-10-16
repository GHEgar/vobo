from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from urllib.parse import quote

from sqlalchemy import ColumnElement, Select, or_, select
from sqlalchemy.orm import Session

from app.core.time import como_utc
from app.models.proyecto import Proyecto
from app.models.ronda import Ronda
from app.schemas.actividad import EventoActividad, UsuarioEvento
from app.services.contenido import Contenido

LARGO_COMENTARIO = 280


@dataclass
class Contexto:
    db: Session
    contenido: Contenido
    proyecto: Proyecto
    limite: int
    usuario: str | None = None
    ronda: int | None = None
    hasta: datetime | None = None
    desempate: str = ""
    nombres: dict[str, str] = field(default_factory=dict)

    def admite(self, evento: EventoActividad) -> bool:
        if self.hasta is None:
            return True
        return (evento.cuando, evento.id) < (self.hasta, self.desempate)

    def ruta(self, camino: str) -> str:
        if self.proyecto.por_omision:
            return camino
        separador = "&" if "?" in camino else "?"
        return f"{camino}{separador}proyecto={quote(self.proyecto.clave)}"

    def persona(self, email: str, nombre: str = "") -> UsuarioEvento:
        return UsuarioEvento(email=email, nombre=self.nombres.get(email) or nombre or email)

    def caso(self, caso_id: str | None) -> dict[str, Any]:
        ubicado = self.contenido.casos.get(caso_id) if caso_id else None
        return {
            "caso_id": caso_id,
            "caso_titulo": ubicado.caso.titulo if ubicado else None,
            "seccion_id": ubicado.seccion_id if ubicado else None,
        }

    def ruta_caso(self, caso_id: str, paso: int | None = None) -> str:
        camino = f"/caso/{quote(caso_id, safe='')}"
        return self.ruta(f"{camino}?paso={paso}" if paso else camino)

    def rondas(self) -> Select:
        if self.ronda is not None:
            return select(Ronda.id).where(
                Ronda.id == self.ronda, Ronda.proyecto_id == self.proyecto.id
            )
        return select(Ronda.id).where(Ronda.proyecto_id == self.proyecto.id)

    def de_persona(self, consulta: Select, columna: ColumnElement[Any]) -> Select:
        return consulta if self.usuario is None else consulta.where(columna == self.usuario)

    def paginar(
        self, consulta: Select, columna: ColumnElement[Any], orden: ColumnElement[Any]
    ) -> list[Any]:
        criterio = (columna.desc(), orden.desc())
        tope = self.limite + 1
        if self.hasta is None:
            return list(self.db.execute(consulta.order_by(*criterio).limit(tope)).all())
        empatados = self.db.execute(consulta.where(columna == self.hasta)).all()
        anteriores = self.db.execute(
            consulta.where(columna < self.hasta).order_by(*criterio).limit(tope)
        ).all()
        return [*empatados, *anteriores]


def cuando(valor: datetime) -> datetime:
    return como_utc(valor) or valor


def clave(tipo: str, *partes: int) -> str:
    return ":".join([tipo, *(f"{p:010d}" for p in partes)])


def recortar(texto: str | None) -> str | None:
    limpio = (texto or "").strip()
    if not limpio:
        return None
    return limpio if len(limpio) <= LARGO_COMENTARIO else f"{limpio[: LARGO_COMENTARIO - 1]}…"


def de_proyecto_o_global(columna: ColumnElement[Any], proyecto_id: int) -> ColumnElement[bool]:
    return or_(columna == proyecto_id, columna.is_(None))


Fuente = Callable[[Contexto], list[EventoActividad]]
