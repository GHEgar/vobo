from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.resultado import Resultado
from app.models.seguimiento import PASO_NO_PUDE, ComentarioSeguimiento
from app.schemas.resultado import normalizar_pasos
from app.schemas.seguimiento import ComentarioUpdate
from app.services import seguimiento

OBJETO = "comentario"
RESUELTO = "resuelto"
CAMPOS = ("resuelto_en", "resuelto_por")


def textos(estado: str | None, pasos: object, comentario: str | None) -> dict[tuple, str]:
    encontrados: dict[tuple, str] = {}
    for marcado in normalizar_pasos(pasos or []):
        if not isinstance(marcado, dict) or not isinstance(marcado.get("paso"), int):
            continue
        texto = (marcado.get("comentario") or "").strip()
        if texto:
            encontrados[(marcado["paso"], "paso")] = texto
    if estado == "no_pude" and comentario:
        encontrados[(PASO_NO_PUDE, "no_pude")] = comentario
    return encontrados


def de_resultados(db: Session, ronda_ids: set[int]) -> dict[tuple, ComentarioSeguimiento]:
    if not ronda_ids:
        return {}
    consulta = select(ComentarioSeguimiento).where(ComentarioSeguimiento.ronda_id.in_(ronda_ids))
    return {
        (f.ronda_id, f.caso_id, f.usuario_email, f.paso, f.tipo): f for f in db.scalars(consulta)
    }


def sincronizar(db: Session, resultado: Resultado, antes: dict[tuple, str]) -> None:
    ahora = textos(resultado.estado, resultado.pasos_marcados, resultado.comentario)
    if not ahora:
        return
    consulta = select(ComentarioSeguimiento).where(
        ComentarioSeguimiento.ronda_id == resultado.ronda_id,
        ComentarioSeguimiento.caso_id == resultado.caso_id,
        ComentarioSeguimiento.usuario_email == resultado.usuario_email,
    )
    filas = {(f.paso, f.tipo): f for f in db.scalars(consulta)}
    for (paso, tipo), texto in ahora.items():
        fila = filas.get((paso, tipo))
        if fila is None:
            db.add(
                ComentarioSeguimiento(
                    ronda_id=resultado.ronda_id,
                    caso_id=resultado.caso_id,
                    usuario_email=resultado.usuario_email,
                    paso=paso,
                    tipo=tipo,
                    estado="nuevo",
                    creado=resultado.actualizado,
                )
            )
        elif texto != antes.get((paso, tipo)) and fila.estado == RESUELTO:
            seguimiento.cambiar_estado(
                db, OBJETO, fila, "nuevo", resultado.usuario_email, RESUELTO, CAMPOS
            )


def obtener_o_404(db: Session, comentario_id: int) -> ComentarioSeguimiento:
    fila = db.get(ComentarioSeguimiento, comentario_id)
    if fila is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comentario no encontrado"
        )
    return fila


def actualizar(
    db: Session, comentario_id: int, cambios: ComentarioUpdate, actor: str
) -> ComentarioSeguimiento:
    fila = obtener_o_404(db, comentario_id)
    if cambios.estado is not None:
        seguimiento.cambiar_estado(db, OBJETO, fila, cambios.estado, actor, RESUELTO, CAMPOS)
    if "plazo" in cambios.model_fields_set:
        seguimiento.cambiar_plazo(db, OBJETO, fila, cambios.plazo, actor)
    db.commit()
    db.refresh(fila)
    return fila
