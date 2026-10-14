from collections import Counter

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.time import utcnow
from app.models.decision import Decision
from app.models.falla import SEVERIDADES, Falla
from app.models.ronda import Ronda
from app.schemas.herramienta import (
    Caracteristica,
    DecisionResponse,
    DecisionUpdate,
    HerramientaResumen,
)
from app.services.consolidado import por_caso, resultados_de_ronda
from app.services.contenido import Contenido

ESTADOS = ("pendiente", "pasa", "falla", "no_pude")


LIMITE_NO_PUDE = 0.2


def sugerir(estados: list[str], abiertas: Counter) -> tuple[str, str]:
    total = len(estados)
    pendientes = estados.count("pendiente")
    graves = abiertas.get("critica", 0) + abiertas.get("alta", 0)
    menores = abiertas.get("media", 0) + abiertas.get("baja", 0)
    no_pude = estados.count("no_pude")
    if not total or pendientes:
        return "sin_probar", f"Faltan {pendientes or total} de {total} casos por probar"
    if graves:
        return "aplazar", f"{graves} falla(s) crítica(s) o alta(s) abierta(s)"
    if no_pude / total > LIMITE_NO_PUDE:
        return "aplazar", f"{no_pude} de {total} casos sin poder probar (más del 20 %)"
    if menores:
        return "desplegar_con_aviso", f"Solo fallas menores abiertas: {menores} media(s) o baja(s)"
    return "desplegar", "Todos los casos probados y sin fallas graves abiertas"


def decisiones_de_ronda(db: Session, ronda_id: int) -> dict[str, Decision]:
    consulta = select(Decision).where(Decision.ronda_id == ronda_id)
    return {d.herramienta_id: d for d in db.scalars(consulta)}


def resumir(db: Session, contenido: Contenido, ronda: Ronda) -> list[HerramientaResumen]:
    consolidados = por_caso(contenido, resultados_de_ronda(db, ronda.id))
    fallas = db.scalars(
        select(Falla).where(
            Falla.ronda_id == ronda.id, Falla.estado != "cerrada", Falla.tipo != "no_pude"
        )
    ).all()
    decisiones = decisiones_de_ronda(db, ronda.id)
    audiencias = {s.id: s.audiencia for s in contenido.respuesta.secciones}
    resumen = []
    for herramienta_id, ubicada in contenido.herramientas.items():
        casos = [cid for cid, u in contenido.casos.items() if u.caso.herramienta == herramienta_id]
        estados = [consolidados[cid] for cid in casos]
        abiertas = Counter(f.severidad for f in fallas if f.caso_id in set(casos))
        por_caso_abiertas = Counter(f.caso_id for f in fallas)
        decision = decisiones.get(herramienta_id)
        sugerencia, motivo = sugerir(estados, abiertas)
        resumen.append(
            HerramientaResumen(
                id=herramienta_id,
                nombre=ubicada.herramienta.nombre or herramienta_id,
                hoy=ubicada.herramienta.hoy,
                seccion_id=ubicada.seccion_id,
                seccion_titulo=ubicada.seccion_titulo,
                audiencia=audiencias.get(ubicada.seccion_id, "funcional"),
                sistema=ubicada.sistema,
                casos_total=len(casos),
                casos={estado: estados.count(estado) for estado in ESTADOS},
                fallas_abiertas={s: abiertas.get(s, 0) for s in SEVERIDADES},
                sugerencia=sugerencia,
                sugerencia_motivo=motivo,
                decision=DecisionResponse.model_validate(decision) if decision else None,
                caracteristicas=[
                    Caracteristica(
                        caso_id=cid,
                        titulo=contenido.casos[cid].caso.titulo,
                        estado=consolidados[cid],
                        fallas_abiertas=por_caso_abiertas.get(cid, 0),
                    )
                    for cid in casos
                ],
            )
        )
    return resumen


def decidir(
    db: Session, contenido: Contenido, herramienta_id: str, datos: DecisionUpdate, email: str
) -> Decision:
    if herramienta_id not in contenido.herramientas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Herramienta no encontrada"
        )
    decision = decisiones_de_ronda(db, datos.ronda_id).get(herramienta_id)
    if decision is None:
        decision = Decision(ronda_id=datos.ronda_id, herramienta_id=herramienta_id)
        db.add(decision)
    decision.decision = datos.decision
    decision.motivo = datos.motivo.strip()
    decision.decidido_por = email
    decision.actualizado = utcnow()
    db.commit()
    db.refresh(decision)
    return decision
