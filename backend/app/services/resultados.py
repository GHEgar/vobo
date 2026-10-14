from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.time import utcnow
from app.models.resultado import Resultado
from app.schemas.resultado import PasoMarcado


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
    if resultado is None:
        resultado = Resultado(ronda_id=ronda_id, caso_id=caso_id, usuario_email=email)
        db.add(resultado)
    resultado.estado = estado
    if pasos_marcados is not None:
        resultado.pasos_marcados = pasos_marcados
        resultado.comentario = (comentario or "").strip() or None
    resultado.actualizado = utcnow()
    db.flush()
    return resultado


def de_usuario(db: Session, ronda_id: int, email: str) -> list[Resultado]:
    consulta = select(Resultado).where(
        Resultado.ronda_id == ronda_id, Resultado.usuario_email == email
    )
    return list(db.scalars(consulta).all())
