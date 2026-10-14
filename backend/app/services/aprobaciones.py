from collections import defaultdict

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.aprobacion import Aprobacion
from app.schemas.aprobacion import (
    AprobacionCreate,
    AprobacionesResponse,
    AprobacionRegistro,
    EstadoCaracteristica,
    EstadoHerramienta,
)
from app.services.contenido import Contenido


def _historiales(db: Session, ronda_id: int) -> dict[tuple[str, str], list[Aprobacion]]:
    consulta = select(Aprobacion).where(Aprobacion.ronda_id == ronda_id).order_by(Aprobacion.id)
    historiales: dict[tuple[str, str], list[Aprobacion]] = defaultdict(list)
    for registro in db.scalars(consulta):
        historiales[(registro.tipo, registro.objetivo_id)].append(registro)
    return historiales


def efectivo_de_caracteristica(
    explicitas: list[Aprobacion], de_herramienta: Aprobacion | None
) -> tuple[str, str, Aprobacion | None]:
    explicita = explicitas[-1] if explicitas else None
    if explicita and (de_herramienta is None or explicita.id > de_herramienta.id):
        return explicita.estado, "explicita", explicita
    if de_herramienta is not None and de_herramienta.estado == "rechazada":
        return "rechazada", "herramienta", de_herramienta
    if explicita:
        return explicita.estado, "explicita", explicita
    if de_herramienta is not None and de_herramienta.estado == "aprobada":
        return "aprobada", "herramienta", de_herramienta
    return "pendiente", "ninguna", None


def _estado_de_herramienta(propia: Aprobacion | None, estados: list[str]) -> str:
    if "aprobada" in estados and "rechazada" in estados:
        return "aprobada_parcial"
    if propia is not None:
        return propia.estado
    if estados and all(e == "aprobada" for e in estados):
        return "aprobada"
    if estados and all(e == "rechazada" for e in estados):
        return "rechazada"
    return "pendiente"


def _registro(aprobacion: Aprobacion | None) -> AprobacionRegistro | None:
    return AprobacionRegistro.model_validate(aprobacion) if aprobacion else None


def estado(db: Session, contenido: Contenido, ronda_id: int) -> AprobacionesResponse:
    historiales = _historiales(db, ronda_id)
    herramientas = []
    for herramienta_id in contenido.herramientas:
        propio = historiales.get(("herramienta", herramienta_id), [])
        propia = propio[-1] if propio else None
        caracteristicas = []
        for caso_id, ubicado in contenido.casos.items():
            if ubicado.caso.herramienta != herramienta_id:
                continue
            explicitas = historiales.get(("caracteristica", caso_id), [])
            valor, origen, actual = efectivo_de_caracteristica(explicitas, propia)
            caracteristicas.append(
                EstadoCaracteristica(
                    caso_id=caso_id,
                    estado=valor,
                    origen=origen,
                    actual=_registro(actual),
                    historial=[_registro(r) for r in explicitas],
                )
            )
        herramientas.append(
            EstadoHerramienta(
                herramienta_id=herramienta_id,
                estado=_estado_de_herramienta(propia, [c.estado for c in caracteristicas]),
                actual=_registro(propia),
                historial=[_registro(r) for r in propio],
                caracteristicas=caracteristicas,
            )
        )
    return AprobacionesResponse(ronda_id=ronda_id, herramientas=herramientas)


def _validar(contenido: Contenido, tipo: str, objetivo_id: str) -> None:
    if tipo == "herramienta" and objetivo_id in contenido.herramientas:
        return
    ubicado = contenido.casos.get(objetivo_id)
    if tipo == "caracteristica" and ubicado and ubicado.caso.herramienta in contenido.herramientas:
        return
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"No existe {tipo} «{objetivo_id}»"
    )


def registrar(
    db: Session, contenido: Contenido, email: str, nombre: str, datos: AprobacionCreate
) -> None:
    for item in datos.items:
        _validar(contenido, item.tipo, item.objetivo_id)
    db.add_all(
        Aprobacion(
            ronda_id=datos.ronda_id,
            tipo=item.tipo,
            objetivo_id=item.objetivo_id,
            estado=item.estado,
            comentario=item.comentario.strip(),
            usuario_email=email,
            usuario_nombre=nombre,
        )
        for item in datos.items
    )
    db.commit()
