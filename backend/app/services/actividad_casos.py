from sqlalchemy import func, select

from app.models.falla import Evidencia, Falla
from app.models.resultado import Resultado
from app.schemas.actividad import EventoActividad
from app.schemas.resultado import normalizar_pasos
from app.services.actividad_fuentes import (
    Contexto,
    clave,
    cuando,
    recortar,
)

TANDA = 200
ESTADOS = {"pasa": "Pasa", "falla": "Falla", "no_pude": "No pude"}
SEVERIDADES = {"critica": "crítica", "alta": "alta", "media": "media", "baja": "baja"}


def _ultimo_paso(pasos: list[dict]) -> int | None:
    marcados = [p["paso"] for p in pasos if isinstance(p, dict) and "paso" in p]
    return max(marcados) + 1 if marcados else None


def _evento_resultado(ctx: Contexto, fila: Resultado, pasos: list[dict]) -> EventoActividad:
    paso = _ultimo_paso(pasos)
    estado = ESTADOS.get(fila.estado)
    if estado:
        resumen = f"Marcó {estado}"
    else:
        resumen = f"Avanzó hasta el paso {paso}" if paso else "Guardó su avance"
    return EventoActividad(
        id=clave("resultado", fila.id),
        tipo="resultado",
        cuando=cuando(fila.actualizado),
        usuario=ctx.persona(fila.usuario_email),
        resumen=resumen,
        **ctx.caso(fila.caso_id),
        paso=paso,
        ronda_id=fila.ronda_id,
        ruta=ctx.ruta_caso(fila.caso_id, paso),
        estado=fila.estado,
        comentario=recortar(fila.comentario),
    )


def _eventos_comentario(ctx: Contexto, fila: Resultado, pasos: list[dict]) -> list[EventoActividad]:
    eventos = []
    for marcado in pasos:
        texto = recortar(marcado.get("comentario") if isinstance(marcado, dict) else None)
        if not texto:
            continue
        paso = marcado["paso"] + 1
        eventos.append(
            EventoActividad(
                id=clave("comentario", fila.id, paso),
                tipo="comentario",
                cuando=cuando(fila.actualizado),
                usuario=ctx.persona(fila.usuario_email),
                resumen=f"Comentó el paso {paso}",
                **ctx.caso(fila.caso_id),
                paso=paso,
                ronda_id=fila.ronda_id,
                ruta=ctx.ruta_caso(fila.caso_id, paso),
                estado=marcado.get("estado"),
                comentario=texto,
                aproximado=True,
            )
        )
    return eventos


def _de_resultados(ctx: Contexto, comentarios: bool) -> list[EventoActividad]:
    consulta = ctx.de_persona(
        select(Resultado).where(Resultado.ronda_id.in_(ctx.rondas())), Resultado.usuario_email
    )
    if ctx.hasta is not None:
        consulta = consulta.where(Resultado.actualizado <= ctx.hasta)
    consulta = consulta.order_by(Resultado.actualizado.desc(), Resultado.id.desc())
    eventos: list[EventoActividad] = []
    desplazamiento = 0
    while True:
        filas = list(ctx.db.scalars(consulta.offset(desplazamiento).limit(TANDA)))
        for fila in filas:
            pasos = normalizar_pasos(fila.pasos_marcados or [])
            nuevos = (
                _eventos_comentario(ctx, fila, pasos)
                if comentarios
                else [_evento_resultado(ctx, fila, pasos)]
            )
            eventos.extend(e for e in nuevos if ctx.admite(e))
        if len(eventos) > ctx.limite or len(filas) < TANDA:
            return eventos
        desplazamiento += TANDA


def resultados(ctx: Contexto) -> list[EventoActividad]:
    return _de_resultados(ctx, comentarios=False)


def comentarios(ctx: Contexto) -> list[EventoActividad]:
    return _de_resultados(ctx, comentarios=True)


def fallas(ctx: Contexto) -> list[EventoActividad]:
    capturas = (
        select(func.count(Evidencia.id))
        .where(Evidencia.falla_id == Falla.id)
        .correlate(Falla)
        .scalar_subquery()
    )
    consulta = ctx.de_persona(
        select(Falla, capturas).where(Falla.ronda_id.in_(ctx.rondas())), Falla.usuario_email
    )
    eventos = []
    for falla, total in ctx.paginar(consulta, Falla.creada, Falla.id):
        paso = falla.paso + 1 if falla.paso is not None else None
        if falla.tipo == "no_pude":
            resumen = "Reportó que no pudo completar el caso"
        else:
            resumen = f"Reportó una falla {SEVERIDADES.get(falla.severidad, falla.severidad)}"
        eventos.append(
            EventoActividad(
                id=clave("falla", falla.id),
                tipo="falla",
                cuando=cuando(falla.creada),
                usuario=ctx.persona(falla.usuario_email),
                resumen=resumen,
                **ctx.caso(falla.caso_id),
                paso=paso,
                ronda_id=falla.ronda_id,
                ruta=ctx.ruta("/fallas"),
                estado=falla.tipo,
                severidad=falla.severidad,
                capturas=total,
            )
        )
    return eventos
