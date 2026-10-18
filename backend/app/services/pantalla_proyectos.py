from collections import Counter
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.time import como_utc, utcnow
from app.models.falla import Falla
from app.models.presencia import Presencia
from app.models.proyecto import Proyecto
from app.models.resultado import Resultado
from app.models.ronda import Ronda
from app.schemas.contenido import Seccion
from app.schemas.pantalla import (
    CasoGrafo,
    Conteos,
    ProyectoPantalla,
    RondaPantalla,
    SeccionGrafo,
    SistemaGrafo,
)
from app.services import proyectos as servicio_proyectos
from app.services.consolidado import por_caso, resultados_de_ronda
from app.services.contenido import Contenido
from app.services.pantalla_identidad import color_de_proyecto
from app.services.presencia import ACTIVO

UMBRAL_CASOS = 120


@dataclass
class Fuente:
    proyecto: Proyecto
    contenido: Contenido
    ronda: Ronda | None
    resultados: list[Resultado]
    color: str


def elegidos(db: Session, claves: list[str]) -> list[tuple[Proyecto, str]]:
    todos = servicio_proyectos.ordenados(db, con_archivados=True)
    colores = {p.id: color_de_proyecto(p.color_nombre, i) for i, p in enumerate(todos)}
    activos = [p for p in todos if not p.archivado]
    if claves:
        posicion = {c: i for i, c in enumerate(claves)}
        activos = sorted(
            (p for p in activos if p.clave in posicion), key=lambda p: posicion[p.clave]
        )
    return [(p, colores[p.id]) for p in activos]


def ronda_abierta(db: Session, proyecto_id: int) -> Ronda | None:
    consulta = (
        select(Ronda)
        .where(Ronda.proyecto_id == proyecto_id, Ronda.abierta.is_(True))
        .order_by(Ronda.id.desc())
        .limit(1)
    )
    return db.scalar(consulta)


def fuente(db: Session, proyecto: Proyecto, contenido: Contenido, color: str) -> Fuente:
    ronda = ronda_abierta(db, proyecto.id)
    resultados = resultados_de_ronda(db, ronda.id) if ronda else []
    return Fuente(proyecto, contenido, ronda, resultados, color)


def _conteos(estados: list[str]) -> Conteos:
    cuenta = Counter(estados)
    return Conteos(
        pasa=cuenta["pasa"],
        falla=cuenta["falla"],
        no_pude=cuenta["no_pude"],
        pendiente=cuenta["pendiente"],
    )


def _avance(conteos: Conteos) -> float:
    total = conteos.pasa + conteos.falla + conteos.no_pude + conteos.pendiente
    return round((total - conteos.pendiente) / total, 4) if total else 0.0


def _seccion(seccion: Seccion, estados: dict[str, str], agrupado: bool) -> SeccionGrafo:
    propios = [(c.id, estados.get(c.id, "pendiente")) for c in seccion.casos]
    conteos = _conteos([e for _, e in propios])
    return SeccionGrafo(
        id=seccion.id,
        titulo=seccion.titulo,
        avance=_avance(conteos),
        conteos=conteos,
        casos=None if agrupado else [CasoGrafo(id=c, estado=e) for c, e in propios],
    )


def _sistemas(
    contenido: Contenido, estados: dict[str, str], agrupado: bool, nombres: dict[str, str]
) -> list[SistemaGrafo]:
    por_sistema: dict[str, list[SeccionGrafo]] = {}
    for seccion in contenido.respuesta.secciones:
        if not seccion.casos:
            continue
        por_sistema.setdefault(seccion.sistema, []).append(_seccion(seccion, estados, agrupado))
    return [SistemaGrafo(nombre=nombres.get(n, n), secciones=s) for n, s in por_sistema.items()]


def _fallas_abiertas(db: Session, ronda: Ronda | None) -> int:
    if ronda is None:
        return 0
    consulta = select(func.count(Falla.id)).where(
        Falla.ronda_id == ronda.id, Falla.tipo != "no_pude", Falla.estado != "cerrada"
    )
    return int(db.scalar(consulta) or 0)


def _en_linea(db: Session, proyecto_id: int) -> int:
    consulta = select(func.count()).where(
        Presencia.proyecto_id == proyecto_id, Presencia.actualizado >= utcnow() - ACTIVO
    )
    return int(db.scalar(consulta) or 0)


def _ronda(ronda: Ronda | None) -> RondaPantalla | None:
    if ronda is None:
        return None
    creada = como_utc(ronda.creada) or utcnow()
    return RondaPantalla(nombre=ronda.nombre, dia=max(1, (utcnow() - creada).days + 1))


def resumen(db: Session, datos: Fuente, nombres: dict[str, str]) -> ProyectoPantalla:
    estados = por_caso(datos.contenido, datos.resultados)
    conteos = _conteos(list(estados.values()))
    agrupado = len(estados) > UMBRAL_CASOS
    return ProyectoPantalla(
        clave=datos.proyecto.clave,
        nombre=datos.proyecto.nombre,
        color=datos.color,
        ronda=_ronda(datos.ronda),
        conteos=conteos,
        total=len(estados),
        avance=_avance(conteos),
        fallas_abiertas=_fallas_abiertas(db, datos.ronda),
        en_linea=_en_linea(db, datos.proyecto.id),
        agrupado=agrupado,
        sistemas=_sistemas(datos.contenido, estados, agrupado, nombres),
    )
