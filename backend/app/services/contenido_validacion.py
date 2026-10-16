import re
from collections.abc import Iterable

from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.contenido import ContenidoProcedimiento, ContenidoSeccion
from app.schemas.contenido import HERRAMIENTA_GENERAL, Procedimiento, Seccion
from app.services import contenido_referencias as referencias

SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,119}$")
ID_CASO = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,59}$")

Error = dict[str, object]


def error(loc: Iterable[object], msg: str) -> Error:
    return {"loc": list(loc), "msg": msg}


def invalido(errores: list[Error]) -> HTTPException:
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=errores)


def conflicto(mensajes: list[str]) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail="; ".join(mensajes))


def _de_pydantic(falla: ValidationError) -> list[Error]:
    return [error(e["loc"], e["msg"]) for e in falla.errors()]


def _ids_unicos(valores: list[str], prefijo: str, nombre: str) -> list[Error]:
    return [
        error([prefijo, i, "id"], f"{nombre} {v} está repetido")
        for i, v in enumerate(valores)
        if valores.index(v) != i
    ]


def _ajenos(db: Session, proyecto_id: int, seccion_id: str) -> tuple[set[str], set[str]]:
    casos: set[str] = set()
    herramientas: set[str] = set()
    for datos in db.scalars(
        select(ContenidoSeccion.datos).where(
            ContenidoSeccion.proyecto_id == proyecto_id, ContenidoSeccion.id != seccion_id
        )
    ):
        casos |= referencias.casos_de(datos)
        herramientas |= referencias.herramientas_de(datos)
    return casos, herramientas - {HERRAMIENTA_GENERAL}


def _referencias(seccion: Seccion, procedimientos: set[str], sistemas: set[str]) -> list[Error]:
    errores = []
    if sistemas and seccion.sistema not in sistemas:
        errores.append(
            error(["sistema"], f"El sistema {seccion.sistema} no existe en la instancia")
        )
    herramientas = {h.id for h in seccion.herramientas}
    for i, item in enumerate(seccion.media):
        if item.procedimiento not in procedimientos:
            errores.append(error(["media", i, "procedimiento"], "Ese procedimiento no existe"))
    for i, caso in enumerate(seccion.casos):
        if not ID_CASO.match(caso.id):
            errores.append(error(["casos", i, "id"], "Usa letras, números, guiones o puntos"))
        if caso.herramienta not in herramientas:
            errores.append(
                error(["casos", i, "herramienta"], "La herramienta no está en la sección")
            )
        for j, paso in enumerate(caso.pasos):
            if paso.procedimiento and paso.procedimiento not in procedimientos:
                errores.append(
                    error(["casos", i, "pasos", j, "procedimiento"], "Ese procedimiento no existe")
                )
            if not paso.texto.strip():
                errores.append(error(["casos", i, "pasos", j, "texto"], "El paso necesita texto"))
    return errores


def seccion(db: Session, proyecto_id: int, datos: dict, sistemas: set[str]) -> Seccion:
    try:
        validada = Seccion.model_validate(datos)
    except ValidationError as falla:
        raise invalido(_de_pydantic(falla)) from None
    errores = (
        [] if SLUG.match(validada.id) else [error(["id"], "Usa minúsculas, números y guiones")]
    )
    if not validada.titulo.strip():
        errores.append(error(["titulo"], "La sección necesita título"))
    casos = [c.id for c in validada.casos]
    herramientas = [h.id for h in validada.herramientas]
    errores += _ids_unicos(casos, "casos", "El caso")
    errores += _ids_unicos(herramientas, "herramientas", "La herramienta")
    casos_ajenos, herramientas_ajenas = _ajenos(db, proyecto_id, validada.id)
    errores += [
        error(["casos", i, "id"], f"El caso {c} ya existe en otra sección")
        for i, c in enumerate(casos)
        if c in casos_ajenos
    ]
    errores += [
        error(["herramientas", i, "id"], f"La herramienta {h} ya existe en otra sección")
        for i, h in enumerate(herramientas)
        if h in herramientas_ajenas
    ]
    procedimientos = set(
        db.scalars(
            select(ContenidoProcedimiento.id).where(
                ContenidoProcedimiento.proyecto_id == proyecto_id
            )
        )
    )
    errores += _referencias(validada, procedimientos, sistemas)
    if errores:
        raise invalido(errores)
    return validada


def procedimiento(datos: dict) -> Procedimiento:
    try:
        validado = Procedimiento.model_validate(datos)
    except ValidationError as falla:
        raise invalido(_de_pydantic(falla)) from None
    if not SLUG.match(validado.id):
        raise invalido([error(["id"], "Usa minúsculas, números y guiones")])
    pasos = datos.get("pasos", [])
    if not isinstance(pasos, list) or not all(isinstance(p, str) for p in pasos):
        raise invalido([error(["pasos"], "Los pasos deben ser una lista de textos")])
    return validado


def normalizar_seccion(validada: Seccion) -> dict:
    datos = validada.model_dump(mode="json")
    for item in datos["media"]:
        item.pop("url", None)
    if validada.oculta:
        datos["oculta"] = True
    return datos


def normalizar_procedimiento(validado: Procedimiento) -> dict:
    return validado.model_dump(mode="json", exclude={"url"})
