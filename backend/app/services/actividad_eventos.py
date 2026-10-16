from sqlalchemy import func, select

from app.core.config import settings
from app.models.aprobacion import Aprobacion
from app.models.aviso import Aviso
from app.models.contenido import ContenidoVersion
from app.models.decision import Decision
from app.models.falla import Falla
from app.models.usuario import Sesion, Usuario
from app.schemas.actividad import EventoActividad
from app.services.actividad_casos import comentarios, fallas, resultados
from app.services.actividad_fuentes import (
    Contexto,
    Fuente,
    clave,
    cuando,
    de_proyecto_o_global,
    recortar,
)

APROBACIONES = {"aprobada": "Aprobó", "rechazada": "Rechazó", "pendiente": "Dejó pendiente"}
DECISIONES = {
    "desplegar": "desplegar",
    "desplegar_con_aviso": "desplegar con aviso",
    "aplazar": "aplazar",
    "pendiente": "pendiente",
}
VERBOS = {
    "crear": "Creó",
    "editar": "Editó",
    "borrar": "Borró",
    "restaurar": "Restauró",
    "ocultar": "Ocultó",
    "mostrar": "Mostró",
    "ordenar": "Reordenó",
    "subir": "Subió",
    "reemplazar": "Reemplazó",
}
OBJETOS = {
    "seccion": "la sección",
    "procedimiento": "el procedimiento",
    "media": "la animación de",
}


def _objetivo(ctx: Contexto, fila: Aprobacion) -> tuple[str, dict]:
    if fila.tipo == "herramienta":
        ubicada = ctx.contenido.herramientas.get(fila.objetivo_id)
        nombre = ubicada.herramienta.nombre if ubicada else ""
        return f"la herramienta {nombre or fila.objetivo_id}", {}
    datos = ctx.caso(fila.objetivo_id)
    return f"la característica {fila.objetivo_id}", datos


def aprobaciones(ctx: Contexto) -> list[EventoActividad]:
    consulta = ctx.de_persona(
        select(Aprobacion).where(Aprobacion.ronda_id.in_(ctx.rondas())), Aprobacion.usuario_email
    )
    eventos = []
    for (fila,) in ctx.paginar(consulta, Aprobacion.creada, Aprobacion.id):
        objetivo, caso = _objetivo(ctx, fila)
        eventos.append(
            EventoActividad(
                id=clave("aprobacion", fila.id),
                tipo="aprobacion",
                cuando=cuando(fila.creada),
                usuario=ctx.persona(fila.usuario_email, fila.usuario_nombre),
                resumen=f"{APROBACIONES.get(fila.estado, fila.estado)} {objetivo}",
                **caso,
                ronda_id=fila.ronda_id,
                ruta=ctx.ruta("/aprobaciones"),
                estado=fila.estado,
                comentario=recortar(fila.comentario),
            )
        )
    return eventos


def decisiones(ctx: Contexto) -> list[EventoActividad]:
    consulta = ctx.de_persona(
        select(Decision).where(Decision.ronda_id.in_(ctx.rondas()), Decision.decidido_por != ""),
        Decision.decidido_por,
    )
    eventos = []
    for (fila,) in ctx.paginar(consulta, Decision.actualizado, Decision.id):
        ubicada = ctx.contenido.herramientas.get(fila.herramienta_id)
        nombre = (ubicada.herramienta.nombre if ubicada else "") or fila.herramienta_id
        eventos.append(
            EventoActividad(
                id=clave("decision", fila.id),
                tipo="decision",
                cuando=cuando(fila.actualizado),
                usuario=ctx.persona(fila.decidido_por),
                resumen=f"Decidió {DECISIONES.get(fila.decision, fila.decision)} {nombre}",
                ronda_id=fila.ronda_id,
                ruta=ctx.ruta("/herramientas"),
                estado=fila.decision,
                comentario=recortar(fila.motivo),
            )
        )
    return eventos


def avisos(ctx: Contexto) -> list[EventoActividad]:
    segundo = func.strftime("%Y-%m-%d %H:%M:%S", Aviso.creado)
    agrupados = ctx.de_persona(
        select(
            func.min(Aviso.id).label("id"),
            func.max(Aviso.creado).label("cuando"),
            func.count(Aviso.id).label("total"),
            Aviso.autor_email,
            func.max(Aviso.autor_nombre).label("autor_nombre"),
            Aviso.titulo,
            Aviso.caso_id,
        ).where(de_proyecto_o_global(Aviso.proyecto_id, ctx.proyecto.id)),
        Aviso.autor_email,
    )
    if ctx.ronda is not None:
        de_ronda = select(Falla.id).where(Falla.ronda_id.in_(ctx.rondas()))
        agrupados = agrupados.where(Aviso.falla_id.in_(de_ronda))
    agrupados = agrupados.group_by(
        Aviso.autor_email, Aviso.titulo, Aviso.mensaje, Aviso.falla_id, Aviso.caso_id, segundo
    ).subquery()
    eventos = []
    for fila in ctx.paginar(select(agrupados), agrupados.c.cuando, agrupados.c.id):
        personas = "1 persona" if fila.total == 1 else f"{fila.total} personas"
        eventos.append(
            EventoActividad(
                id=clave("aviso", fila.id),
                tipo="aviso",
                cuando=cuando(fila.cuando),
                usuario=ctx.persona(fila.autor_email, fila.autor_nombre),
                resumen=f"Envió el aviso «{fila.titulo}» a {personas}",
                **ctx.caso(fila.caso_id),
                ruta=ctx.ruta_caso(fila.caso_id) if fila.caso_id else None,
            )
        )
    return eventos


def sesiones(ctx: Contexto) -> list[EventoActividad]:
    if ctx.ronda is not None:
        return []
    consulta = ctx.de_persona(
        select(Sesion.created_at, Usuario.id, Usuario.email, Usuario.nombre).join(
            Usuario, Usuario.id == Sesion.usuario_id
        ),
        Usuario.email,
    )
    return [
        EventoActividad(
            id=clave("sesion", fila.id, int(cuando(fila.created_at).timestamp() * 1e6)),
            tipo="sesion",
            cuando=cuando(fila.created_at),
            usuario=ctx.persona(fila.email, fila.nombre),
            resumen="Inició sesión",
        )
        for fila in ctx.paginar(consulta, Sesion.created_at, Usuario.id)
    ]


def _titulo_seccion(ctx: Contexto, seccion_id: str) -> str:
    return next((s.titulo for s in ctx.contenido.respuesta.secciones if s.id == seccion_id), "")


def contenido(ctx: Contexto) -> list[EventoActividad]:
    if ctx.ronda is not None or not settings.contenido_en_base:
        return []
    consulta = ctx.de_persona(
        select(
            ContenidoVersion.id,
            ContenidoVersion.tipo,
            ContenidoVersion.objeto_id,
            ContenidoVersion.accion,
            ContenidoVersion.autor_email,
            ContenidoVersion.creado,
        ).where(ContenidoVersion.proyecto_id == ctx.proyecto.id),
        ContenidoVersion.autor_email,
    )
    eventos = []
    for fila in ctx.paginar(consulta, ContenidoVersion.creado, ContenidoVersion.id):
        es_seccion = fila.tipo == "seccion"
        titulo = _titulo_seccion(ctx, fila.objeto_id) if es_seccion else ""
        objeto = OBJETOS.get(fila.tipo, fila.tipo)
        verbo = VERBOS.get(fila.accion, fila.accion.capitalize())
        visible = es_seccion and fila.accion != "borrar" and titulo
        eventos.append(
            EventoActividad(
                id=clave("contenido", fila.id),
                tipo="contenido",
                cuando=cuando(fila.creado),
                usuario=ctx.persona(fila.autor_email),
                resumen=f"{verbo} {objeto} «{titulo or fila.objeto_id}»",
                seccion_id=fila.objeto_id if es_seccion else None,
                ruta=ctx.ruta(f"/seccion/{fila.objeto_id}") if visible else None,
                estado=fila.accion,
            )
        )
    return eventos


FUENTES: dict[str, Fuente] = {
    "resultado": resultados,
    "falla": fallas,
    "comentario": comentarios,
    "aprobacion": aprobaciones,
    "decision": decisiones,
    "aviso": avisos,
    "sesion": sesiones,
    "contenido": contenido,
}
