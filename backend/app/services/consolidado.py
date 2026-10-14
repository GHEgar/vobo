from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.resultado import Resultado
from app.services.contenido import Contenido

EJECUTADO = frozenset({"pasa", "falla"})


def consolidar(estados: list[str]) -> str:
    for estado in ("falla", "pasa", "no_pude"):
        if estado in estados:
            return estado
    return "pendiente"


def por_caso(contenido: Contenido, resultados: list[Resultado]) -> dict[str, str]:
    estados: dict[str, list[str]] = defaultdict(list)
    for resultado in resultados:
        estados[resultado.caso_id].append(resultado.estado)
    return {cid: consolidar(estados.get(cid, [])) for cid in contenido.casos}


def resultados_de_ronda(db: Session, ronda_id: int) -> list[Resultado]:
    return list(db.scalars(select(Resultado).where(Resultado.ronda_id == ronda_id)))
