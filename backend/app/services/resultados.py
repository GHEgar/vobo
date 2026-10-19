from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.time import utcnow
from app.models.resultado import Resultado, ResultadoHistorial
from app.schemas.resultado import PasoMarcado, normalizar_pasos
from app.services import comentarios_seguimiento


def limpiar_pasos(pasos: list[PasoMarcado], total: int) -> list[dict]:
    por_paso = {p.paso: p for p in pasos if 0 <= p.paso < total}
    return [
        {
            "paso": p.paso,
            "estado": p.estado,
            "comentario": (p.comentario or "").strip() or None,
        }
        for p in sorted(por_paso.values(), key=lambda p: p.paso)
    ]


def _por_paso(pasos: object) -> dict[int, tuple]:
    normalizados = normalizar_pasos(pasos or [])
    return {
        p["paso"]: (p.get("estado"), p.get("comentario"))
        for p in normalizados
        if isinstance(p, dict) and "paso" in p
    }


def _accion(previo: str | None, nuevo: str, pasos_cambiaron: bool) -> str | None:
    if previo != nuevo and nuevo == "pendiente" and previo is not None:
        return "limpiar"
    if previo != nuevo and nuevo != "pendiente":
        return "marcar" if previo in (None, "pendiente") else "cambiar"
    if pasos_cambiaron:
        return "paso"
    return "crear" if previo is None else None


def _registrar(
    db: Session, resultado: Resultado, previo: str | None, pasos_previos: object
) -> None:
    antes, despues = _por_paso(pasos_previos), _por_paso(resultado.pasos_marcados)
    cambiados = sorted(n for n in set(antes) | set(despues) if antes.get(n) != despues.get(n))
    accion = _accion(previo, resultado.estado, bool(cambiados))
    if accion is None:
        return
    db.add(
        ResultadoHistorial(
            ronda_id=resultado.ronda_id,
            caso_id=resultado.caso_id,
            usuario_email=resultado.usuario_email,
            estado=resultado.estado,
            paso=cambiados[0] if len(cambiados) == 1 else None,
            accion=accion,
            creado=resultado.actualizado,
        )
    )


def guardar(
    db: Session,
    ronda_id: int,
    caso_id: str,
    email: str,
    estado: str,
    pasos_marcados: list[dict] | None = None,
    comentario: str | None = None,
) -> Resultado:
    resultado = db.scalar(
        select(Resultado).where(
            Resultado.ronda_id == ronda_id,
            Resultado.caso_id == caso_id,
            Resultado.usuario_email == email,
        )
    )
    previo = None if resultado is None else resultado.estado
    pasos_previos = [] if resultado is None else resultado.pasos_marcados
    antes = (
        {}
        if resultado is None
        else comentarios_seguimiento.textos(previo, pasos_previos, resultado.comentario)
    )
    if resultado is None:
        resultado = Resultado(ronda_id=ronda_id, caso_id=caso_id, usuario_email=email)
        db.add(resultado)
    resultado.estado = estado
    if pasos_marcados is not None:
        resultado.pasos_marcados = pasos_marcados
        resultado.comentario = (comentario or "").strip() or None
    resultado.actualizado = utcnow()
    _registrar(db, resultado, previo, pasos_previos)
    comentarios_seguimiento.sincronizar(db, resultado, antes)
    db.flush()
    return resultado


def de_usuario(db: Session, ronda_id: int, email: str) -> list[Resultado]:
    consulta = select(Resultado).where(
        Resultado.ronda_id == ronda_id, Resultado.usuario_email == email
    )
    return list(db.scalars(consulta).all())
