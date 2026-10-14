from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.resultado import Resultado
from app.models.ronda import Ronda
from app.models.usuario import Usuario
from app.schemas.resultado import ComentarioResponse, normalizar_pasos
from app.services.contenido import Contenido


def listar(
    db: Session,
    contenido: Contenido,
    ronda_id: int | None,
    caso_id: str | None = None,
    email: str | None = None,
) -> list[ComentarioResponse]:
    consulta = select(Resultado).order_by(Resultado.actualizado.desc())
    if ronda_id is not None:
        consulta = consulta.where(Resultado.ronda_id == ronda_id)
    if caso_id is not None:
        consulta = consulta.where(Resultado.caso_id == caso_id)
    if email is not None:
        consulta = consulta.where(Resultado.usuario_email == email)
    nombres = {u.email: u.nombre for u in db.scalars(select(Usuario))}
    rondas = {r.id: r.nombre for r in db.scalars(select(Ronda))}
    comentarios = []
    for resultado in db.scalars(consulta):
        ubicado = contenido.casos.get(resultado.caso_id)
        caso = ubicado.caso if ubicado else None
        base = {
            "ronda_id": resultado.ronda_id,
            "caso_id": resultado.caso_id,
            "caso_titulo": caso.titulo if caso else "",
            "sistema": ubicado.sistema if ubicado else "",
            "usuario_email": resultado.usuario_email,
            "autor": nombres.get(resultado.usuario_email, resultado.usuario_email),
            "ronda_nombre": rondas.get(resultado.ronda_id, ""),
            "actualizado": resultado.actualizado,
        }
        for marcado in normalizar_pasos(resultado.pasos_marcados or []):
            texto = (marcado.get("comentario") or "").strip()
            if not texto:
                continue
            paso = marcado["paso"]
            paso_texto = caso.pasos[paso].texto if caso and paso < len(caso.pasos) else ""
            comentarios.append(
                ComentarioResponse(
                    **base, paso=paso, paso_texto=paso_texto, tipo="paso", comentario=texto
                )
            )
        if resultado.estado == "no_pude" and resultado.comentario:
            comentarios.append(
                ComentarioResponse(
                    **base,
                    paso=None,
                    paso_texto="",
                    tipo="no_pude",
                    comentario=resultado.comentario,
                )
            )
    return sorted(comentarios, key=lambda c: c.actualizado, reverse=True)
