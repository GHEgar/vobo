from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.aprobacion import Aprobacion
from app.models.decision import Decision
from app.models.falla import Falla
from app.models.resultado import Resultado
from app.models.ronda import Asignacion, Ronda


def _del_proyecto(consulta: Select, modelo: type, proyecto_id: int) -> Select:
    return consulta.join(Ronda, Ronda.id == modelo.ronda_id).where(Ronda.proyecto_id == proyecto_id)


def casos_usados(db: Session, proyecto_id: int, ids: set[str]) -> set[str]:
    if not ids:
        return set()
    con_resultado = _del_proyecto(
        select(Resultado.caso_id).where(Resultado.caso_id.in_(ids)), Resultado, proyecto_id
    )
    con_falla = _del_proyecto(
        select(Falla.caso_id).where(Falla.caso_id.in_(ids)), Falla, proyecto_id
    )
    return set(db.scalars(con_resultado)) | set(db.scalars(con_falla))


def herramientas_usadas(db: Session, proyecto_id: int, ids: set[str]) -> set[str]:
    if not ids:
        return set()
    decididas = _del_proyecto(
        select(Decision.herramienta_id).where(Decision.herramienta_id.in_(ids)),
        Decision,
        proyecto_id,
    )
    aprobadas = _del_proyecto(
        select(Aprobacion.objetivo_id).where(
            Aprobacion.tipo == "herramienta", Aprobacion.objetivo_id.in_(ids)
        ),
        Aprobacion,
        proyecto_id,
    )
    return set(db.scalars(decididas)) | set(db.scalars(aprobadas))


def secciones_usadas(db: Session, proyecto_id: int, ids: set[str]) -> set[str]:
    if not ids:
        return set()
    asignadas = _del_proyecto(
        select(Asignacion.seccion_id).where(Asignacion.seccion_id.in_(ids)),
        Asignacion,
        proyecto_id,
    )
    con_falla = _del_proyecto(
        select(Falla.seccion_id).where(Falla.seccion_id.in_(ids)), Falla, proyecto_id
    )
    return set(db.scalars(asignadas)) | set(db.scalars(con_falla))


def casos_de(datos: dict) -> set[str]:
    return {c.get("id") for c in datos.get("casos") or [] if isinstance(c, dict)}


def herramientas_de(datos: dict) -> set[str]:
    return {h.get("id") for h in datos.get("herramientas") or [] if isinstance(h, dict)}


def bloqueos(db: Session, proyecto_id: int, antes: list[dict], despues: list[dict]) -> list[str]:
    def todos(datos: list[dict], de: object) -> set[str]:
        return set().union(*(de(d) for d in datos)) if datos else set()

    mensajes = []
    secciones = {d.get("id") for d in antes} - {d.get("id") for d in despues}
    for seccion in sorted(secciones_usadas(db, proyecto_id, secciones)):
        mensajes.append(
            f"La sección {seccion} tiene asignaciones o fallas; ocúltala en vez de quitarla"
        )
    casos = todos(antes, casos_de) - todos(despues, casos_de)
    for caso in sorted(casos_usados(db, proyecto_id, casos)):
        mensajes.append(
            f"El caso {caso} tiene resultados guardados; no se puede quitar ni renombrar"
        )
    herramientas = todos(antes, herramientas_de) - todos(despues, herramientas_de)
    for herramienta in sorted(herramientas_usadas(db, proyecto_id, herramientas)):
        mensajes.append(
            f"La herramienta {herramienta} tiene decisiones o aprobaciones; no se puede quitar"
        )
    return mensajes
