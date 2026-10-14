from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.falla import SEVERIDADES, Falla
from app.models.resultado import Resultado
from app.models.ronda import Asignacion, Ronda
from app.models.usuario import Usuario
from app.schemas.herramienta import DecisionResponse
from app.schemas.tablero import Celda, ConteoSeveridad, Criterio, FilaPersona, TableroResponse
from app.services import tablero_proyectos, visibilidad
from app.services.consolidado import EJECUTADO, por_caso, resultados_de_ronda
from app.services.contenido import Contenido
from app.services.herramientas import decisiones_de_ronda

FAMILIAS = ("A", "B", "C", "D", "E", "T")
FAMILIAS_ESTRICTAS = frozenset({"B", "D"})


def visibles_por_persona(
    db: Session, contenido: Contenido, ronda_id: int, resultados: list[Resultado], audiencia: str
) -> dict[str, set[str]]:
    asignadas: dict[str, set[str]] = defaultdict(set)
    for asignacion in db.scalars(select(Asignacion).where(Asignacion.ronda_id == ronda_id)):
        asignadas[asignacion.usuario_email].add(asignacion.seccion_id)
    emails = set(asignadas) | {r.usuario_email for r in resultados}
    tecnico = visibilidad.tecnicos(db, emails)
    return (
        {
            email: visibilidad.secciones_visibles(
                contenido, asignadas.get(email, set()), tecnico[email], audiencia
            )
            for email in sorted(emails)
        }
        if emails
        else {}
    )


def _filas(
    db: Session,
    contenido: Contenido,
    resultados: list[Resultado],
    visibles: dict[str, set[str]],
) -> list[FilaPersona]:
    por_persona: dict[str, dict[str, str]] = defaultdict(dict)
    for resultado in resultados:
        por_persona[resultado.usuario_email][resultado.caso_id] = resultado.estado
    emails = list(visibles)
    nombres = {
        u.email: u.nombre for u in db.scalars(select(Usuario).where(Usuario.email.in_(emails)))
    }
    filas = []
    for email in emails:
        secciones = visibles[email]
        estados = por_persona.get(email, {})
        celdas = []
        for familia in FAMILIAS:
            casos = [
                cid
                for cid, u in contenido.casos.items()
                if u.caso.familia == familia and u.seccion_id in secciones
            ]
            marcados = [estados.get(cid, "pendiente") for cid in casos]
            celdas.append(
                Celda(
                    familia=familia,
                    total=len(casos),
                    hechos=sum(1 for e in marcados if e != "pendiente"),
                    pasa=marcados.count("pasa"),
                    falla=marcados.count("falla"),
                    no_pude=marcados.count("no_pude"),
                )
            )
        filas.append(FilaPersona(email=email, nombre=nombres.get(email, email), celdas=celdas))
    return filas


def _criterios(
    contenido: Contenido, fallas: list[Falla], consolidados: dict[str, str]
) -> list[Criterio]:
    abiertas = [f for f in fallas if f.estado != "cerrada"]
    criticas = sum(1 for f in abiertas if f.severidad == "critica")
    altas = sum(
        1
        for f in abiertas
        if f.severidad == "alta"
        and (u := contenido.casos.get(f.caso_id)) is not None
        and u.caso.familia in FAMILIAS_ESTRICTAS
    )
    total = len(consolidados)
    ejecutados = sum(1 for e in consolidados.values() if e in EJECUTADO)
    sin_probar = sum(1 for e in consolidados.values() if e == "pendiente")
    no_pude = sum(1 for e in consolidados.values() if e == "no_pude")
    return [
        Criterio(
            clave="criticas",
            descripcion="Cero fallas críticas abiertas",
            cumple=criticas == 0,
            detalle=f"{criticas} falla(s) crítica(s) abierta(s)",
        ),
        Criterio(
            clave="altas_b_d",
            descripcion="Cero fallas altas abiertas en las familias B y D",
            cumple=altas == 0,
            detalle=f"{altas} falla(s) alta(s) abierta(s) en acceso o respaldos",
        ),
        Criterio(
            clave="ejecucion",
            descripcion="Todos los casos ejecutados",
            cumple=total > 0 and ejecutados == total,
            detalle=(
                f"{ejecutados} de {total} casos ejecutados; {sin_probar} sin probar "
                f"y {no_pude} marcados «No pude probarlo»"
            ),
        ),
    ]


def calcular(
    db: Session, contenido: Contenido, ronda: Ronda, audiencia: str = "todas"
) -> TableroResponse:
    resultados = resultados_de_ronda(db, ronda.id)
    fallas = list(
        db.scalars(select(Falla).where(Falla.ronda_id == ronda.id, Falla.tipo != "no_pude"))
    )
    consolidados = por_caso(contenido, resultados)
    conteo = [
        ConteoSeveridad(
            severidad=severidad,
            abiertas=sum(1 for f in fallas if f.severidad == severidad and f.estado != "cerrada"),
            total=sum(1 for f in fallas if f.severidad == severidad),
        )
        for severidad in SEVERIDADES
    ]
    criterios = _criterios(contenido, fallas, consolidados)
    sale = all(c.cumple for c in criterios)
    visibles = visibles_por_persona(db, contenido, ronda.id, resultados, audiencia)
    visibles = {email: ids for email, ids in visibles.items() if ids}
    por_proyecto, cobertura = tablero_proyectos.calcular(contenido, resultados, visibles, audiencia)
    return TableroResponse(
        ronda_id=ronda.id,
        familias=list(FAMILIAS),
        proyectos=tablero_proyectos.proyectos_con_casos(contenido, audiencia),
        por_proyecto=por_proyecto,
        cobertura=cobertura,
        personas=_filas(db, contenido, resultados, visibles),
        fallas=conteo,
        casos_total=len(consolidados),
        casos_ejecutados=sum(1 for e in consolidados.values() if e in EJECUTADO),
        criterios=criterios,
        veredicto="Sale" if sale else "No sale",
        razones=[c.detalle for c in criterios if not c.cumple],
        decisiones=[
            DecisionResponse.model_validate(d) for d in decisiones_de_ronda(db, ronda.id).values()
        ],
    )
