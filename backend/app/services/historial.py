from collections import Counter
from datetime import UTC, date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.time import como_utc, utcnow
from app.models.resultado import ResultadoHistorial
from app.models.ronda import Ronda
from app.schemas.historial import PuntoAvance

Clave = tuple[int, str, str]


def _dia(momento: datetime) -> date:
    return como_utc(momento).astimezone(UTC).date()


def _eventos(db: Session, rondas: list[int], hasta: date | None) -> list[ResultadoHistorial]:
    consulta = select(ResultadoHistorial).where(ResultadoHistorial.ronda_id.in_(rondas))
    if hasta is not None:
        limite = datetime.combine(hasta + timedelta(days=1), time.min, tzinfo=UTC)
        consulta = consulta.where(ResultadoHistorial.creado < limite)
    return list(db.scalars(consulta.order_by(ResultadoHistorial.creado, ResultadoHistorial.id)))


def _aplicar(evento: ResultadoHistorial, estados: dict[Clave, str], activos: Counter[str]) -> None:
    clave = (evento.ronda_id, evento.caso_id, evento.usuario_email)
    antes = estados.get(clave, "pendiente") != "pendiente"
    ahora = evento.estado != "pendiente"
    estados[clave] = evento.estado
    if ahora and not antes:
        activos[evento.caso_id] += 1
    elif antes and not ahora:
        activos[evento.caso_id] -= 1


def rondas_en_alcance(db: Session, proyecto_id: int, ronda_id: int | None) -> list[int]:
    if ronda_id is not None:
        return [ronda_id]
    return list(db.scalars(select(Ronda.id).where(Ronda.proyecto_id == proyecto_id)))


def avance(
    db: Session,
    rondas: list[int],
    casos: set[str],
    desde: date | None = None,
    hasta: date | None = None,
) -> list[PuntoAvance]:
    eventos = [e for e in _eventos(db, rondas, hasta) if e.caso_id in casos]
    if not eventos:
        return []
    inicio = max(desde or date.min, _dia(eventos[0].creado))
    ultimo = _dia(eventos[-1].creado)
    fin = min(hasta, max(ultimo, utcnow().date())) if hasta else max(ultimo, desde or ultimo)
    estados: dict[Clave, str] = {}
    activos: Counter[str] = Counter()
    puntos: list[PuntoAvance] = []
    indice = 0
    dia = inicio
    while dia <= fin:
        while indice < len(eventos) and _dia(eventos[indice].creado) <= dia:
            _aplicar(eventos[indice], estados, activos)
            indice += 1
        marcados = sum(1 for n in activos.values() if n > 0)
        puntos.append(PuntoAvance(fecha=dia, marcados_acumulados=marcados, total=len(casos)))
        dia += timedelta(days=1)
    return puntos
