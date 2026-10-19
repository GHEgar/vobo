from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.resultado import Resultado
from app.models.ronda import Ronda
from app.models.seguimiento import PASO_NO_PUDE
from app.schemas.resultado import ComentarioResponse, normalizar_pasos
from app.services import comentarios_seguimiento, seguimiento, vinculos
from app.services.contenido import Contenido


def _clave(comentario: ComentarioResponse) -> tuple:
    paso = PASO_NO_PUDE if comentario.paso is None else comentario.paso
    return (
        comentario.ronda_id,
        comentario.caso_id,
        comentario.usuario_email,
        paso,
        comentario.tipo,
    )


def _nombre(conocidos: dict[str, str], email: str | None) -> str:
    return conocidos.get(email, email) if email else ""


def _con_seguimiento(
    db: Session, comentarios: list[ComentarioResponse], conocidos: dict[str, str]
) -> list[ComentarioResponse]:
    filas = comentarios_seguimiento.de_resultados(db, {c.ronda_id for c in comentarios})
    propias = {id(c): filas.get(_clave(c)) for c in comentarios}
    existentes = [f for f in propias.values() if f is not None]
    eventos = seguimiento.de_objetos(db, "comentario", [f.id for f in existentes], conocidos)
    resumen = vinculos.resumen(db, "comentario", existentes)
    enriquecidos = []
    for c in comentarios:
        fila = propias[id(c)]
        if fila is None:
            enriquecidos.append(c)
            continue
        enriquecidos.append(
            c.model_copy(
                update={
                    "id": fila.id,
                    "estado": fila.estado,
                    "plazo": fila.plazo,
                    "plazo_por": fila.plazo_por,
                    "plazo_por_nombre": _nombre(conocidos, fila.plazo_por),
                    "creado": fila.creado,
                    "resuelto_en": fila.resuelto_en,
                    "resuelto_por": fila.resuelto_por,
                    "resuelto_por_nombre": _nombre(conocidos, fila.resuelto_por),
                    "seguimiento": eventos.get(fila.id, []),
                    **resumen[fila.id],
                }
            )
        )
    return enriquecidos


def listar(
    db: Session,
    contenido: Contenido,
    ronda_id: int | None,
    caso_id: str | None = None,
    email: str | None = None,
    proyecto_id: int | None = None,
) -> list[ComentarioResponse]:
    consulta = select(Resultado).order_by(Resultado.actualizado.desc())
    if ronda_id is not None:
        consulta = consulta.where(Resultado.ronda_id == ronda_id)
    elif proyecto_id is not None:
        del_proyecto = select(Ronda.id).where(Ronda.proyecto_id == proyecto_id)
        consulta = consulta.where(Resultado.ronda_id.in_(del_proyecto))
    if caso_id is not None:
        consulta = consulta.where(Resultado.caso_id == caso_id)
    if email is not None:
        consulta = consulta.where(Resultado.usuario_email == email)
    nombres = seguimiento.nombres(db)
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
    ordenados = sorted(comentarios, key=lambda c: c.actualizado, reverse=True)
    return _con_seguimiento(db, ordenados, nombres)
