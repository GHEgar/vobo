from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.falla import Falla
from app.models.proyecto import Proyecto
from app.models.resultado import Resultado
from app.models.ronda import Ronda
from app.services.consolidado import por_caso
from app.services.contenido import Contenido

Agrupar = Literal["proyecto", "sistema", "seccion"]


@dataclass
class Fuente:
    proyecto: Proyecto
    ronda: Ronda | None
    resultados: list[Resultado]
    contenido: Contenido


@dataclass
class Grupo:
    clave: str
    nombre: str
    fuente: Fuente
    estados: list[str] = field(default_factory=list)
    secciones: set[str] = field(default_factory=set)
    fallas_abiertas: int = 0


@dataclass
class Agrupacion:
    grupos: dict[str, Grupo] = field(default_factory=dict)
    marcados: dict[str, dict[str, int]] = field(default_factory=lambda: defaultdict(dict))


def _titulos(fuente: Fuente) -> dict[str, str]:
    return {s.id: s.titulo for s in fuente.contenido.respuesta.secciones}


def _clave(
    fuente: Fuente,
    seccion_id: str,
    sistema: str,
    agrupar: Agrupar,
    varios: bool,
    nombres: dict[str, str],
    titulos: dict[str, str],
) -> tuple[str, str]:
    if agrupar == "proyecto":
        return fuente.proyecto.clave, fuente.proyecto.nombre
    base, nombre = (
        (sistema, nombres.get(sistema, sistema))
        if agrupar == "sistema"
        else (seccion_id, titulos.get(seccion_id, seccion_id))
    )
    if not varios:
        return base, nombre
    return f"{fuente.proyecto.clave}:{base}", f"{nombre} · {fuente.proyecto.nombre}"


def _abiertas(db: Session, ronda: Ronda | None) -> list[str]:
    if ronda is None:
        return []
    consulta = select(Falla.caso_id).where(
        Falla.ronda_id == ronda.id, Falla.tipo != "no_pude", Falla.estado != "cerrada"
    )
    return list(db.scalars(consulta))


def agrupar_fuentes(
    db: Session, fuentes: list[Fuente], agrupar: Agrupar, nombres: dict[str, str]
) -> Agrupacion:
    salida = Agrupacion()
    varios = len(fuentes) > 1
    for fuente in fuentes:
        titulos = _titulos(fuente)
        de_caso: dict[str, str] = {}
        for caso_id, estado in por_caso(fuente.contenido, fuente.resultados).items():
            ubicado = fuente.contenido.casos[caso_id]
            clave, nombre = _clave(
                fuente, ubicado.seccion_id, ubicado.sistema, agrupar, varios, nombres, titulos
            )
            grupo = salida.grupos.setdefault(clave, Grupo(clave, nombre, fuente))
            grupo.estados.append(estado)
            grupo.secciones.add(ubicado.seccion_id)
            de_caso[caso_id] = clave
        for caso_id in _abiertas(db, fuente.ronda):
            if caso_id in de_caso:
                salida.grupos[de_caso[caso_id]].fallas_abiertas += 1
        propios = Counter(
            (r.usuario_email, de_caso[r.caso_id])
            for r in fuente.resultados
            if r.estado != "pendiente" and r.caso_id in de_caso
        )
        for (email, clave), n in propios.items():
            salida.marcados[email][clave] = salida.marcados[email].get(clave, 0) + n
    return salida
