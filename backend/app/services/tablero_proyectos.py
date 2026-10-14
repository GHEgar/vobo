from collections import defaultdict

from app.models.resultado import Resultado
from app.schemas.tablero import CeldaProyecto
from app.services.contenido import Contenido
from app.services.visibilidad import AUDIENCIAS


def proyectos_con_casos(contenido: Contenido, audiencia: str = "todas") -> list[str]:
    return sorted(
        {
            s.sistema
            for s in contenido.respuesta.secciones
            if s.casos and (audiencia not in AUDIENCIAS or s.audiencia == audiencia)
        }
    )


def calcular(
    contenido: Contenido,
    resultados: list[Resultado],
    visibles: dict[str, set[str]],
    audiencia: str = "todas",
) -> tuple[dict[str, dict[str, CeldaProyecto]], dict[str, int]]:
    estados: dict[str, dict[str, str]] = defaultdict(dict)
    for resultado in resultados:
        estados[resultado.usuario_email][resultado.caso_id] = resultado.estado
    proyectos = proyectos_con_casos(contenido, audiencia)
    por_proyecto: dict[str, dict[str, CeldaProyecto]] = {}
    cobertura = dict.fromkeys(proyectos, 0)
    for email, secciones in visibles.items():
        propios = estados.get(email, {})
        celdas = {}
        for sistema in proyectos:
            del_proyecto = [
                u
                for u in contenido.casos.values()
                if u.sistema == sistema and u.seccion_id in secciones
            ]
            marcados = [propios.get(u.caso.id, "pendiente") for u in del_proyecto]
            asignado = bool(del_proyecto)
            cobertura[sistema] += int(asignado)
            celdas[sistema] = CeldaProyecto(
                hechos=sum(1 for e in marcados if e != "pendiente"),
                total=len(del_proyecto),
                falla=marcados.count("falla"),
                asignado=asignado,
            )
        por_proyecto[email] = celdas
    return por_proyecto, cobertura
