from collections import defaultdict
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.time import utcnow
from app.models.presencia import Presencia
from app.models.usuario import Usuario
from app.schemas.actividad import EventoActividad
from app.schemas.pantalla import ActualPersona, EventoPantalla, PersonaPantalla
from app.services import actividad, tablero
from app.services.pantalla_identidad import (
    color_de_persona,
    id_de_persona,
    iniciales,
    nombre_de_pila,
)
from app.services.pantalla_proyectos import Fuente
from app.services.presencia import ACTIVO

LIMITE_EVENTOS = 20
TIPOS_EVENTO = ["resultado", "falla", "aprobacion"]
ESTADOS = {"pasa": "Pasa", "falla": "Falla", "no_pude": "No pude"}


@dataclass
class Acumulado:
    participa: dict[str, int] = field(default_factory=dict)
    marcados: int = 0
    asignados: int = 0
    actual: ActualPersona | None = None
    activa: bool = False


def _presencias(db: Session, fuentes: list[Fuente]) -> list[Presencia]:
    ids = [f.proyecto.id for f in fuentes]
    consulta = select(Presencia).where(
        Presencia.actualizado >= utcnow() - ACTIVO, Presencia.proyecto_id.in_(ids)
    )
    return list(db.scalars(consulta))


def _sumar_proyecto(db: Session, datos: Fuente, gente: dict[str, Acumulado]) -> None:
    if datos.ronda is None:
        return
    propios: dict[str, dict[str, str]] = defaultdict(dict)
    for resultado in datos.resultados:
        propios[resultado.usuario_email][resultado.caso_id] = resultado.estado
    for email, estados in propios.items():
        marcados = sum(1 for e in estados.values() if e != "pendiente")
        if marcados:
            gente.setdefault(email, Acumulado()).participa[datos.proyecto.clave] = marcados
    visibles = tablero.visibles_por_persona(
        db, datos.contenido, datos.ronda.id, datos.resultados, "todas"
    )
    for email, secciones in visibles.items():
        if email not in gente or not secciones:
            continue
        casos = [c for c, u in datos.contenido.casos.items() if u.seccion_id in secciones]
        estados = propios.get(email, {})
        gente[email].asignados += len(casos)
        gente[email].marcados += sum(1 for c in casos if estados.get(c, "pendiente") != "pendiente")


def _marcar_presentes(fuentes: list[Fuente], presentes: list[Presencia], gente: dict) -> None:
    por_id = {f.proyecto.id: f for f in fuentes}
    for fila in presentes:
        datos = por_id.get(fila.proyecto_id)
        if datos is None:
            continue
        acumulado = gente.setdefault(fila.usuario_email, Acumulado())
        acumulado.activa = True
        ubicado = datos.contenido.casos.get(fila.caso_id) if fila.caso_id else None
        seccion = fila.seccion_id or (ubicado.seccion_id if ubicado else None)
        if ubicado or seccion:
            acumulado.actual = ActualPersona(
                proyecto=datos.proyecto.clave,
                caso_id=fila.caso_id if ubicado else None,
                seccion_id=seccion,
            )


def personas(db: Session, fuentes: list[Fuente]) -> list[PersonaPantalla]:
    gente: dict[str, Acumulado] = {}
    presentes = _presencias(db, fuentes)
    _marcar_presentes(fuentes, presentes, gente)
    for datos in fuentes:
        _sumar_proyecto(db, datos, gente)
    emails = list(gente)
    nombres = {
        u.email: u.nombre for u in db.scalars(select(Usuario).where(Usuario.email.in_(emails)))
    }
    nombres.update({p.usuario_email: p.nombre for p in presentes if p.nombre})
    lista = []
    for email in sorted(emails, key=lambda e: nombre_de_pila(nombres.get(e, ""))):
        acumulado = gente[email]
        nombre = nombres.get(email, "")
        lista.append(
            PersonaPantalla(
                id=id_de_persona(email),
                nombre=nombre_de_pila(nombre),
                iniciales=iniciales(nombre),
                color=color_de_persona(email),
                activa=acumulado.activa,
                participa=acumulado.participa,
                marcados=acumulado.marcados,
                asignados=acumulado.asignados,
                avance=round(acumulado.marcados / acumulado.asignados, 4)
                if acumulado.asignados
                else 0.0,
                actual=acumulado.actual,
            )
        )
    return lista


def _texto(evento: EventoActividad) -> str | None:
    caso = evento.caso_id or ""
    if evento.tipo == "resultado":
        if evento.estado in ESTADOS:
            return f"marcó {caso} · {ESTADOS[evento.estado]}"
        return f"va en {caso} · paso {evento.paso}" if evento.paso else f"avanzó en {caso}"
    if evento.tipo == "falla":
        if evento.estado == "no_pude":
            return f"no pudo completar {caso}"
        return f"reportó una falla en {caso}"
    if evento.tipo == "aprobacion":
        return evento.resumen[:1].lower() + evento.resumen[1:80]
    return None


def eventos(db: Session, fuentes: list[Fuente]) -> list[EventoPantalla]:
    todos = []
    for datos in fuentes:
        pagina = actividad.listar(
            db,
            datos.contenido,
            datos.proyecto,
            LIMITE_EVENTOS,
            tipos=TIPOS_EVENTO,
            ronda=datos.ronda.id if datos.ronda else None,
        )
        for evento in pagina.eventos:
            texto = _texto(evento)
            if texto is None:
                continue
            todos.append(
                EventoPantalla(
                    id=f"{datos.proyecto.clave}:{evento.id}",
                    quien=nombre_de_pila(evento.usuario.nombre),
                    color=datos.color,
                    proyecto=datos.proyecto.clave,
                    texto=texto,
                    cuando=evento.cuando,
                )
            )
    todos.sort(key=lambda e: (e.cuando, e.id), reverse=True)
    return todos[:LIMITE_EVENTOS]
