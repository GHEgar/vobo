import logging
from pathlib import Path
from typing import Any

from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.time import utcnow
from app.models.configuracion import Configuracion
from app.models.contenido import ContenidoSeccion
from app.schemas.configuracion import (
    CAMPOS,
    FUENTES,
    RANURAS,
    TOKENS,
    ArchivoDeMarca,
    ConfiguracionCambios,
    ConfiguracionResponse,
)
from app.schemas.instancia import Instancia, InstanciaResponse, LogoResponse
from app.services import contenido, marca
from app.services import instancia as instancias

logger = logging.getLogger("validacion.configuracion")

SIMPLES = ("producto", "nombre", "descripcion", "entrada", "color_tema", "proyectos", "cuentas")
FAMILIAS = {"producto": "'Rotulo', system-ui, sans-serif", "sistema": "system-ui, sans-serif"}
PESOS = ("negrita", "media", "regular")


def _filas(db: Session) -> dict[str, Configuracion]:
    return {f.clave: f for f in db.scalars(select(Configuracion))}


def _validos(filas: dict[str, Configuracion]) -> dict[str, Any]:
    valores: dict[str, Any] = {}
    for clave, fila in filas.items():
        if clave not in CAMPOS:
            continue
        try:
            leido = ConfiguracionCambios.model_validate({clave: fila.valor})
        except ValidationError as error:
            logger.warning("configuración %s inválida, se ignora: %s", clave, error)
            continue
        valores[clave] = getattr(leido, clave)
    return valores


def _marca(filas: dict[str, Configuracion]) -> dict[str, ArchivoDeMarca]:
    archivos = {}
    for ranura in RANURAS:
        fila = filas.get(ranura)
        if fila is None or not isinstance(fila.valor, dict):
            continue
        datos = fila.valor
        archivos[ranura] = ArchivoDeMarca(
            **datos, url=marca.url(str(datos["archivo"]), str(datos["huella"]))
        )
    return archivos


def leer(db: Session | None = None) -> tuple[dict[str, Any], dict[str, ArchivoDeMarca]]:
    if db is None:
        with SessionLocal() as propia:
            return leer(propia)
    filas = _filas(db)
    return _validos(filas), _marca(filas)


def base() -> Instancia:
    try:
        return contenido.cargar().instancia
    except ValueError:
        return instancias.leer(Path(settings.contenido_dir), [])


def efectiva(valores: dict[str, Any] | None = None) -> Instancia:
    if valores is None:
        valores = leer()[0]
    return base().model_copy(update={c: valores[c] for c in SIMPLES if c in valores})


def _logo(
    original: LogoResponse | None, valores: dict[str, Any], archivos: dict[str, ArchivoDeMarca]
) -> LogoResponse | None:
    claro = archivos.get("logo_claro")
    oscuro = archivos.get("logo_oscuro")
    if original is None and claro is None and oscuro is None:
        return None
    url_claro = claro.url if claro else original.claro if original else oscuro.url
    url_oscuro = oscuro.url if oscuro else claro.url if claro else original.oscuro
    alt = valores.get("logo_alt") or (original.alt if original else "")
    return LogoResponse(claro=url_claro, oscuro=url_oscuro, alt=alt)


def respuesta(db: Session | None = None) -> InstanciaResponse:
    valores, archivos = leer(db)
    instancia = efectiva(valores)
    original = instancias.respuesta(instancia)
    logo = _logo(original.logo, valores, archivos)
    if logo is not None and not logo.alt:
        logo = logo.model_copy(update={"alt": instancia.producto})
    favicon = archivos["favicon"].url if "favicon" in archivos else original.favicon
    return original.model_copy(update={"logo": logo, "favicon": favicon})


def _colores_de_archivos(instancia: Instancia) -> dict[str, str]:
    return {"nombre": instancia.color_nombre} if instancia.color_nombre else {}


def _colores(valores: dict[str, Any]) -> dict[str, str]:
    return {**_colores_de_archivos(base()), **valores.get("colores", {})}


def css(db: Session | None = None) -> str:
    valores = leer(db)[0]
    lineas = [f"    --color-{t}: {c};" for t, c in _colores(valores).items()]
    familia = FAMILIAS.get(valores.get("fuente", "tema"))
    if familia:
        lineas += [f"    --tipo-{peso}: {familia};" for peso in PESOS]
    return ":root {\n" + "\n".join(lineas) + "\n}\n" if lineas else ""


def en_uso(db: Session) -> set[str]:
    if settings.contenido_en_base:
        filas = db.scalars(select(ContenidoSeccion.datos))
        return {str(d.get("sistema")) for d in filas if isinstance(d, dict) and d.get("sistema")}
    try:
        return {s.sistema for s in contenido.cargar().respuesta.secciones}
    except ValueError:
        return set()


def _proteger_proyectos(db: Session, nuevos: list[str]) -> None:
    actuales = {p.clave for p in efectiva(leer(db)[0]).proyectos}
    quitados = sorted((actuales - set(nuevos)) & en_uso(db))
    if quitados:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Hay secciones que usan {', '.join(quitados)}; no se puede quitar",
        )


def _fijar(db: Session, clave: str, valor: object, autor: str) -> None:
    fila = db.get(Configuracion, clave)
    if fila is None:
        fila = Configuracion(clave=clave)
        db.add(fila)
    fila.valor = valor
    fila.actualizado = utcnow()
    fila.autor_email = autor


def guardar(db: Session, cambios: ConfiguracionCambios, autor: str) -> None:
    datos = cambios.model_dump(mode="json", include=cambios.model_fields_set)
    if "proyectos" in datos:
        _proteger_proyectos(db, [p["clave"] for p in datos["proyectos"]])
    for clave, valor in datos.items():
        _fijar(db, clave, valor, autor)
    db.commit()


def restablecer(db: Session, clave: str) -> None:
    if clave not in CAMPOS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campo desconocido")
    fila = db.get(Configuracion, clave)
    if fila is None:
        return
    if clave == "proyectos":
        valores = {k: v for k, v in leer(db)[0].items() if k != "proyectos"}
        _proteger_proyectos(db, [p.clave for p in efectiva(valores).proyectos])
    db.delete(fila)
    db.commit()


def subir(db: Session, ranura: str, contenido_archivo: bytes, autor: str) -> None:
    mime, extension = marca.validar(contenido_archivo)
    nombre = f"{ranura}.{extension}"
    anterior = db.get(Configuracion, ranura)
    marca.escribir(nombre, contenido_archivo)
    if anterior is not None and anterior.valor.get("archivo") != nombre:
        marca.quitar(str(anterior.valor.get("archivo")))
    valor = {
        "archivo": nombre,
        "mime": mime,
        "tamano": len(contenido_archivo),
        "huella": marca.huella(contenido_archivo),
    }
    _fijar(db, ranura, valor, autor)
    db.commit()


def quitar_archivo(db: Session, ranura: str) -> None:
    fila = db.get(Configuracion, ranura)
    if fila is None:
        return
    marca.quitar(str(fila.valor.get("archivo")))
    db.delete(fila)
    db.commit()


def servir(db: Session, nombre: str, version: str | None) -> tuple[bytes, str, bool] | None:
    archivos = leer(db)[1]
    vigente = next((a for a in archivos.values() if a.archivo == nombre), None)
    leido = marca.leer(nombre) if vigente else None
    if vigente is None or leido is None:
        return None
    return leido[0], leido[1], version == vigente.huella[:16]


def _archivos(instancia: Instancia) -> dict[str, object]:
    original = instancias.respuesta(instancia)
    return {
        **original.model_dump(include={"producto", "nombre", "descripcion", "color_tema"}),
        "entrada": instancia.entrada.model_dump(),
        "logo_alt": instancia.logo.alt if instancia.logo else "",
        "logo": original.logo.model_dump() if original.logo else None,
        "favicon": original.favicon,
        "proyectos": [p.model_dump() for p in instancia.proyectos],
        "cuentas": [c.model_dump() for c in instancia.cuentas],
        "colores": _colores_de_archivos(instancia),
        "fuente": "tema",
    }


def estado(db: Session) -> ConfiguracionResponse:
    valores, archivos = leer(db)
    guardada = ConfiguracionCambios.model_validate(valores).model_dump(
        mode="json", include=set(valores)
    )
    return ConfiguracionResponse(
        guardada=guardada,
        archivos=_archivos(base()),
        marca=archivos,
        efectiva=respuesta(db),
        colores=valores.get("colores", {}),
        fuente=valores.get("fuente", "tema"),
        tokens=list(TOKENS),
        fuentes=list(FUENTES),
        proyectos_en_uso=sorted(en_uso(db)),
    )
