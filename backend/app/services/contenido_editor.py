import copy

from fastapi import HTTPException, status
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.time import utcnow
from app.models.contenido import ContenidoSeccion
from app.schemas.contenido import HERRAMIENTA_GENERAL
from app.schemas.editor import SeccionDetalle, SeccionResumen
from app.services import configuracion
from app.services import contenido_referencias as referencias
from app.services import contenido_validacion as validacion
from app.services import contenido_versiones as versiones


def exigir_base() -> None:
    if not settings.contenido_en_base:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El contenido de esta instancia se gestiona por archivos",
        )


def sistemas() -> set[str]:
    return {p.clave for p in configuracion.efectiva().proyectos}


def seccion_o_404(db: Session, proyecto_id: int, seccion_id: str) -> ContenidoSeccion:
    fila = db.get(ContenidoSeccion, {"proyecto_id": proyecto_id, "id": seccion_id})
    if fila is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sección no encontrada")
    return fila


def _usados(
    db: Session, proyecto_id: int, filas: list[ContenidoSeccion]
) -> tuple[set[str], set[str], set[str]]:
    casos = set().union(*(referencias.casos_de(f.datos) for f in filas)) if filas else set()
    herramientas = (
        set().union(*(referencias.herramientas_de(f.datos) for f in filas)) if filas else set()
    )
    return (
        referencias.secciones_usadas(db, proyecto_id, {f.id for f in filas}),
        referencias.casos_usados(db, proyecto_id, casos),
        referencias.herramientas_usadas(db, proyecto_id, herramientas),
    )


def _del_proyecto(proyecto_id: int) -> Select:
    return select(ContenidoSeccion).where(ContenidoSeccion.proyecto_id == proyecto_id)


def listar(db: Session, proyecto_id: int) -> list[SeccionResumen]:
    orden = (ContenidoSeccion.orden, ContenidoSeccion.id)
    filas = list(db.scalars(_del_proyecto(proyecto_id).order_by(*orden)))
    secciones, casos, _ = _usados(db, proyecto_id, filas)
    return [
        SeccionResumen(
            id=f.id,
            orden=f.orden,
            titulo=str(f.datos.get("titulo", "")),
            sistema=str(f.datos.get("sistema", "")),
            audiencia=str(f.datos.get("audiencia") or "funcional"),
            oculta=bool(f.datos.get("oculta", False)),
            casos=len(f.datos.get("casos") or []),
            con_resultados=f.id in secciones or bool(referencias.casos_de(f.datos) & casos),
            actualizado=f.actualizado,
            autor_email=f.autor_email,
        )
        for f in filas
    ]


def detalle(db: Session, fila: ContenidoSeccion) -> SeccionDetalle:
    secciones, casos, herramientas = _usados(db, fila.proyecto_id, [fila])
    return SeccionDetalle(
        id=fila.id,
        datos=fila.datos,
        actualizado=fila.actualizado,
        autor_email=fila.autor_email,
        con_resultados=bool(secciones or casos),
        casos_bloqueados=sorted(casos),
        herramientas_bloqueadas=sorted(herramientas),
    )


def _escribir(db: Session, fila: ContenidoSeccion, datos: dict, autor: str) -> ContenidoSeccion:
    fila.datos = datos
    fila.orden = datos.get("orden", 0)
    fila.actualizado = utcnow()
    fila.autor_email = autor
    db.commit()
    return fila


def crear(
    db: Session, proyecto_id: int, datos: dict, autor: str, accion: str = "crear"
) -> ContenidoSeccion:
    if not datos.get("orden"):
        maximo = select(func.max(ContenidoSeccion.orden)).where(
            ContenidoSeccion.proyecto_id == proyecto_id
        )
        datos = {**datos, "orden": (db.scalar(maximo) or 0) + 10}
    validada = validacion.seccion(db, proyecto_id, datos, sistemas())
    if db.get(ContenidoSeccion, {"proyecto_id": proyecto_id, "id": validada.id}) is not None:
        raise validacion.invalido([validacion.error(["id"], "Ya existe una sección con ese id")])
    fila = ContenidoSeccion(proyecto_id=proyecto_id, id=validada.id)
    db.add(fila)
    versiones.registrar(db, proyecto_id, "seccion", validada.id, accion, None, autor)
    return _escribir(db, fila, validacion.normalizar_seccion(validada), autor)


def guardar(
    db: Session, fila: ContenidoSeccion, datos: dict, autor: str, accion: str = "editar"
) -> ContenidoSeccion:
    if datos.get("id") != fila.id:
        raise validacion.invalido([validacion.error(["id"], "El id de la sección no cambia")])
    validada = validacion.seccion(db, fila.proyecto_id, datos, sistemas())
    nuevos = validacion.normalizar_seccion(validada)
    bloqueos = referencias.bloqueos(db, fila.proyecto_id, [fila.datos], [nuevos])
    if bloqueos:
        raise validacion.conflicto(bloqueos)
    if nuevos == fila.datos:
        return fila
    versiones.registrar(db, fila.proyecto_id, "seccion", fila.id, accion, fila.datos, autor)
    return _escribir(db, fila, nuevos, autor)


def borrar(db: Session, fila: ContenidoSeccion, autor: str) -> None:
    bloqueos = referencias.bloqueos(db, fila.proyecto_id, [fila.datos], [])
    if bloqueos:
        raise validacion.conflicto(bloqueos)
    versiones.registrar(db, fila.proyecto_id, "seccion", fila.id, "borrar", fila.datos, autor)
    db.delete(fila)
    db.commit()


def ocultar(db: Session, fila: ContenidoSeccion, oculta: bool, autor: str) -> ContenidoSeccion:
    datos = {k: v for k, v in fila.datos.items() if k != "oculta"}
    if oculta:
        datos["oculta"] = True
    if datos == fila.datos:
        return fila
    accion = "ocultar" if oculta else "mostrar"
    versiones.registrar(db, fila.proyecto_id, "seccion", fila.id, accion, fila.datos, autor)
    return _escribir(db, fila, datos, autor)


def _libre(base: str, ocupados: set[str], largo: int) -> str:
    candidato = base[:largo]
    numero = 2
    while candidato in ocupados:
        sufijo = str(numero)
        candidato = f"{base[: largo - len(sufijo)]}{sufijo}"
        numero += 1
    ocupados.add(candidato)
    return candidato


def duplicar(db: Session, fila: ContenidoSeccion, nuevo_id: str, autor: str) -> ContenidoSeccion:
    todas = list(
        db.scalars(
            select(ContenidoSeccion.datos).where(ContenidoSeccion.proyecto_id == fila.proyecto_id)
        )
    )
    casos = set().union(*(referencias.casos_de(d) for d in todas))
    herramientas = set().union(*(referencias.herramientas_de(d) for d in todas))
    datos = copy.deepcopy(fila.datos)
    datos.pop("oculta", None)
    datos.update(id=nuevo_id, titulo=f"{datos.get('titulo', '')} (copia)", orden=fila.orden + 1)
    renombradas = {}
    for herramienta in datos.get("herramientas") or []:
        if herramienta.get("id") != HERRAMIENTA_GENERAL:
            nuevo = _libre(f"{herramienta['id']}-copia", herramientas, 120)
            renombradas[herramienta["id"]] = nuevo
            herramienta["id"] = nuevo
    for caso in datos.get("casos") or []:
        caso["id"] = _libre(f"{caso['id']}-COPIA", casos, 60)
        if caso.get("herramienta") in renombradas:
            caso["herramienta"] = renombradas[caso["herramienta"]]
    return crear(db, fila.proyecto_id, datos, autor)


def ordenar(db: Session, proyecto_id: int, ids: list[str], autor: str) -> None:
    filas = {f.id: f for f in db.scalars(_del_proyecto(proyecto_id))}
    if sorted(ids) != sorted(filas):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="El orden debe incluir todas las secciones una sola vez",
        )
    for posicion, seccion_id in enumerate(ids, start=1):
        fila = filas[seccion_id]
        if fila.orden == posicion * 10 and fila.datos.get("orden") == posicion * 10:
            continue
        versiones.registrar(db, proyecto_id, "seccion", fila.id, "ordenar", fila.datos, autor)
        fila.datos = {**fila.datos, "orden": posicion * 10}
        fila.orden = posicion * 10
        fila.actualizado = utcnow()
        fila.autor_email = autor
    db.commit()
