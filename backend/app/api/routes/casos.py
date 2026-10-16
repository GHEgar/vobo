from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import Actor, get_actor, require_permission
from app.core.database import get_db
from app.core.permisos import EJECUTAR_CASOS
from app.models.resultado import Resultado
from app.schemas.resultado import MisCasosResponse, ResultadoResponse, ResultadoUpdate
from app.services import contenido, proyectos, resultados, rondas, visibilidad

router = APIRouter(prefix="/api", tags=["casos"])


@router.get("/mis-casos", response_model=MisCasosResponse)
def mis_casos(
    ronda: int = Query(...),
    db: Session = Depends(get_db),
    actor: Actor = Depends(get_actor),
) -> MisCasosResponse:
    actual = contenido.obtener(proyectos.de_ronda(db, ronda))
    asignadas = rondas.secciones_asignadas(db, ronda, actor.email)
    visibles = visibilidad.secciones_visibles(
        actual, set(asignadas), actor.ve(visibilidad.PAGINA_TECNICO)
    )
    tecnicas = {s.id for s in actual.respuesta.secciones if s.audiencia == "tecnica"}
    return MisCasosResponse(
        ronda_id=ronda,
        secciones_asignadas=asignadas,
        secciones_visibles=sorted(visibles),
        ve_tecnico=bool(visibles & tecnicas),
        resultados=[
            ResultadoResponse.model_validate(r)
            for r in resultados.de_usuario(db, ronda, actor.email)
            if (u := actual.casos.get(r.caso_id)) is not None and u.seccion_id in visibles
        ],
    )


@router.put("/resultados/{caso_id}", response_model=ResultadoResponse)
def guardar_resultado(
    caso_id: str,
    datos: ResultadoUpdate,
    db: Session = Depends(get_db),
    actor: Actor = Depends(require_permission(EJECUTAR_CASOS)),
) -> Resultado:
    actual = contenido.obtener(proyectos.de_ronda(db, datos.ronda_id))
    ubicado = contenido.caso_o_404(actual, caso_id)
    rondas.abierta_o_409(db, datos.ronda_id)
    pasos = resultados.limpiar_pasos(datos.pasos_marcados, len(ubicado.caso.pasos))
    resultado = resultados.guardar(
        db, datos.ronda_id, caso_id, actor.email, datos.estado, pasos, datos.comentario
    )
    db.commit()
    db.refresh(resultado)
    return resultado
