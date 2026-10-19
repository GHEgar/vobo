import csv
import io
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.time import como_utc
from app.models.ronda import Ronda
from app.models.usuario import Usuario
from app.schemas.falla import FallaResponse
from app.schemas.resultado import ComentarioResponse
from app.services.contenido import Contenido

BOM = "﻿"
PELIGROSOS = ("=", "+", "-", "@", "\t", "\r")
COLUMNAS = (
    "id",
    "ronda",
    "caso",
    "título del caso",
    "sección",
    "herramienta",
    "paso",
    "tipo",
    "severidad",
    "reproducible",
    "estado",
    "reportó",
    "correo",
    "fecha",
    "obtenido",
    "nota de resolución",
    "url",
    "versión visible",
    "navegador",
    "capturas",
    "plazo",
    "responsable",
    "resuelta",
    "resolvió",
    "tiempo de solución (horas)",
    "respuestas",
)
TIPOS = {"falla": "Falla", "no_pude": "No pude probarlo"}
SEVERIDADES = {"critica": "Crítica", "alta": "Alta", "media": "Media", "baja": "Baja"}
REPRODUCIBLE = {"siempre": "Siempre", "a_veces": "A veces", "una_vez": "Una vez"}
ESTADOS = {
    "nueva": "Nueva",
    "en_curso": "En curso",
    "lista_para_revalidar": "Lista para revalidar",
    "cerrada": "Cerrada",
}


def zona(nombre: str | None) -> ZoneInfo:
    try:
        return ZoneInfo(nombre or "UTC")
    except (ZoneInfoNotFoundError, ValueError):
        return ZoneInfo("UTC")


def seguro(valor: object) -> str:
    texto = "" if valor is None else str(valor)
    return f"'{texto}" if texto.startswith(PELIGROSOS) else texto


def fecha_local(momento: datetime, tz: ZoneInfo) -> str:
    return (como_utc(momento) or momento).astimezone(tz).strftime("%Y-%m-%d %H:%M")


def _herramienta(contenido: Contenido, falla: FallaResponse) -> str:
    ubicado = contenido.casos.get(falla.caso_id)
    if ubicado is None:
        return ""
    clave = ubicado.caso.herramienta
    seccion = next((s for s in contenido.respuesta.secciones if s.id == ubicado.seccion_id), None)
    propia = next((h for h in seccion.herramientas if h.id == clave), None) if seccion else None
    ubicada = contenido.herramientas.get(clave)
    herramienta = propia or (ubicada.herramienta if ubicada else None)
    return (herramienta.nombre or herramienta.id) if herramienta else clave


def _paso(falla: FallaResponse) -> str:
    if falla.paso is None:
        return "Fuera de los pasos"
    return f"{falla.paso + 1}. {falla.paso_texto}".strip()


def del_caso(falla: FallaResponse, comentario: ComentarioResponse) -> bool:
    if (comentario.caso_id, comentario.ronda_id) != (falla.caso_id, falla.ronda_id):
        return False
    return falla.paso is None or comentario.paso in (None, falla.paso)


def comentarios_de(
    falla: FallaResponse, comentarios: list[ComentarioResponse], tz: ZoneInfo
) -> str:
    propios = sorted((c for c in comentarios if del_caso(falla, c)), key=lambda c: c.actualizado)
    return "\n".join(
        f"{fecha_local(c.actualizado, tz)} · {c.autor or c.usuario_email}: {c.comentario}"
        for c in propios
    )


def horas(falla: FallaResponse) -> str:
    if falla.resuelta_en is None:
        return ""
    inicio = como_utc(falla.creada) or falla.creada
    fin = como_utc(falla.resuelta_en) or falla.resuelta_en
    return f"{max((fin - inicio).total_seconds(), 0) / 3600:.1f}"


def respuestas_de(falla: FallaResponse, tz: ZoneInfo) -> str:
    return "\n".join(
        f"{fecha_local(e.creado, tz)} · {e.autor or e.autor_email}: {e.texto}"
        for e in falla.seguimiento
        if e.accion == "respuesta"
    )


def _persona(nombres: dict[str, str], email: str | None) -> str:
    return nombres.get(email, email) if email else ""


def generar(
    db: Session,
    contenido: Contenido,
    fallas: list[FallaResponse],
    tz: ZoneInfo,
    comentarios: list[ComentarioResponse] | None = None,
) -> str:
    nombres = {u.email: u.nombre for u in db.scalars(select(Usuario))}
    rondas = {r.id: r.nombre for r in db.scalars(select(Ronda))}
    salida = io.StringIO()
    escritor = csv.writer(salida, lineterminator="\r\n")
    escritor.writerow(COLUMNAS if comentarios is None else (*COLUMNAS, "Comentarios"))
    for f in fallas:
        fila = (
            f.id,
            rondas.get(f.ronda_id, f.ronda_id),
            f.caso_id,
            f.caso_titulo,
            f.seccion_titulo or f.seccion_id,
            _herramienta(contenido, f),
            _paso(f),
            TIPOS.get(f.tipo, f.tipo),
            SEVERIDADES.get(f.severidad, f.severidad),
            "" if f.tipo == "no_pude" else REPRODUCIBLE.get(f.reproducible, f.reproducible),
            ESTADOS.get(f.estado, f.estado),
            nombres.get(f.usuario_email, ""),
            f.usuario_email,
            fecha_local(f.creada, tz),
            f.obtenido,
            f.nota_resolucion,
            f.url,
            f.version_visible,
            f.navegador,
            len(f.evidencias),
            f.plazo.isoformat() if f.plazo else "",
            _persona(nombres, f.plazo_por),
            fecha_local(f.resuelta_en, tz) if f.resuelta_en else "",
            _persona(nombres, f.resuelta_por),
            horas(f),
            respuestas_de(f, tz),
        )
        if comentarios is not None:
            fila = (*fila, comentarios_de(f, comentarios, tz))
        escritor.writerow([seguro(v) for v in fila])
    return BOM + salida.getvalue()


def nombre_archivo(ronda: int | None, tz: ZoneInfo, ahora: datetime) -> str:
    fecha = ahora.astimezone(tz).strftime("%Y-%m-%d")
    return f"fallas-ronda-{ronda}-{fecha}.csv" if ronda is not None else f"fallas-{fecha}.csv"
