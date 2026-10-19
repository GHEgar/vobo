from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from typing import NoReturn

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.falla import Falla
from app.models.ronda import Ronda
from app.models.seguimiento import PASO_NO_PUDE, ComentarioSeguimiento
from app.schemas.seguimiento import PrincipalResponse
from app.services import avisos_seguimiento, seguimiento

Registro = Falla | ComentarioSeguimiento
Referencia = tuple[str, int]

MODELOS: dict[str, type[Falla] | type[ComentarioSeguimiento]] = {
    "falla": Falla,
    "comentario": ComentarioSeguimiento,
}
FINALES = {
    "falla": ("cerrada", ("resuelta_en", "resuelta_por")),
    "comentario": ("resuelto", ("resuelto_en", "resuelto_por")),
}
MAPEO = {
    ("falla", "comentario"): {
        "nueva": "nuevo",
        "en_curso": "en_curso",
        "lista_para_revalidar": "en_curso",
        "cerrada": "resuelto",
    },
    ("comentario", "falla"): {"nuevo": "nueva", "en_curso": "en_curso", "resuelto": "cerrada"},
}


@dataclass(frozen=True)
class Sumas:
    total: float
    pendiente: float


def estado_para(origen: str, destino: str, estado: str) -> str:
    return estado if origen == destino else MAPEO[(origen, destino)][estado]


def clave(objeto: str, objeto_id: int) -> str:
    return f"{objeto}:{objeto_id}"


def etiqueta(objeto: str, registro: Registro | None, objeto_id: int | None = None) -> str:
    if registro is None:
        return f"#{objeto_id}" if objeto == "falla" else f"comentario {objeto_id}"
    if objeto == "falla":
        return f"#{registro.id} · {registro.caso_id}"
    paso = "no pude" if registro.paso == PASO_NO_PUDE else f"paso {registro.paso + 1}"
    return f"{registro.caso_id} · {paso}"


def obtener(db: Session, objeto: str, objeto_id: int) -> Registro | None:
    return db.get(MODELOS[objeto], objeto_id)


def referencia(registro: Registro) -> Referencia | None:
    if registro.principal_id is None or registro.principal_objeto is None:
        return None
    return registro.principal_objeto, registro.principal_id


def _proyecto(db: Session, registro: Registro) -> int | None:
    return db.scalar(select(Ronda.proyecto_id).where(Ronda.id == registro.ronda_id))


def seguidores(db: Session, objeto: str, principal_id: int) -> list[tuple[str, Registro]]:
    encontrados: list[tuple[str, Registro]] = []
    for nombre, modelo in MODELOS.items():
        consulta = (
            select(modelo)
            .where(modelo.principal_objeto == objeto, modelo.principal_id == principal_id)
            .order_by(modelo.id)
        )
        encontrados.extend((nombre, fila) for fila in db.scalars(consulta))
    return encontrados


def conteo_seguidores(db: Session, objeto: str, ids: list[int]) -> dict[int, int]:
    conteo: Counter[int] = Counter()
    if not ids:
        return {}
    for modelo in MODELOS.values():
        consulta = (
            select(modelo.principal_id, func.count())
            .where(modelo.principal_objeto == objeto, modelo.principal_id.in_(ids))
            .group_by(modelo.principal_id)
        )
        for principal_id, cuantos in db.execute(consulta):
            conteo[principal_id] += cuantos
    return dict(conteo)


def _rechazar(detalle: str) -> NoReturn:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detalle)


def _validar(
    db: Session, objeto: str, registro: Registro, destino: Registro, ref: Referencia
) -> None:
    if _proyecto(db, destino) != _proyecto(db, registro):
        _rechazar("El reporte principal es de otro proyecto")
    if referencia(destino) is not None:
        _rechazar(
            f"{etiqueta(ref[0], destino)} ya se resuelve con otro reporte: vincula con su principal"
        )
    cuantos = conteo_seguidores(db, objeto, [registro.id]).get(registro.id, 0)
    if cuantos:
        _rechazar(
            f"Este reporte es principal de {cuantos} "
            f"{'reporte' if cuantos == 1 else 'reportes'}: quita esos vínculos antes"
        )


def vincular(
    db: Session, objeto: str, registro: Registro, principal: Referencia | None, actor: str
) -> bool:
    actual = referencia(registro)
    if principal is None:
        if actual is None:
            return False
        texto = etiqueta(actual[0], obtener(db, *actual), actual[1])
        registro.principal_objeto = None
        registro.principal_id = None
        seguimiento.registrar(
            db, objeto, registro.id, actor, "vinculo", texto, anterior=clave(*actual)
        )
        return True
    if principal == (objeto, registro.id):
        _rechazar("Un reporte no puede resolverse consigo mismo")
    destino = obtener(db, *principal)
    if destino is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="El reporte principal no existe"
        )
    if principal == actual:
        return False
    _validar(db, objeto, registro, destino, principal)
    registro.principal_objeto, registro.principal_id = principal
    texto = etiqueta(principal[0], destino)
    seguimiento.registrar(
        db,
        objeto,
        registro.id,
        actor,
        "vinculo",
        texto,
        anterior=clave(*actual) if actual else None,
        nuevo=clave(*principal),
    )
    seguimiento.cambiar_plazo(db, objeto, registro, destino.plazo, actor, texto)
    return True


def propagar(
    db: Session, objeto: str, principal: Registro, actor: str, estado: bool, plazo: bool
) -> None:
    if not (estado or plazo):
        return
    texto = etiqueta(objeto, principal)
    for destino, fila in seguidores(db, objeto, principal.id):
        previo = fila.estado
        if plazo:
            seguimiento.cambiar_plazo(db, destino, fila, principal.plazo, actor, texto)
        if estado:
            final, campos = FINALES[destino]
            nuevo = estado_para(objeto, destino, principal.estado)
            seguimiento.cambiar_estado(db, destino, fila, nuevo, actor, final, campos, texto)
        if fila.estado != previo:
            avisos_seguimiento.avisar_estado(db, destino, fila, actor)


def principales(db: Session, refs: Iterable[Referencia]) -> dict[Referencia, PrincipalResponse]:
    pedidos = set(refs)
    encontrados = {
        (nombre, fila.id): fila
        for nombre, modelo in MODELOS.items()
        if (ids := [i for o, i in pedidos if o == nombre])
        for fila in db.scalars(select(modelo).where(modelo.id.in_(ids)))
    }
    return {
        ref: PrincipalResponse(
            objeto=ref[0], id=ref[1], etiqueta=etiqueta(ref[0], encontrados.get(ref), ref[1])
        )
        for ref in pedidos
    }


def resumen(db: Session, objeto: str, registros: list[Registro]) -> dict[int, dict]:
    conteos = conteo_seguidores(db, objeto, [r.id for r in registros])
    refs = {r.id: referencia(r) for r in registros}
    conocidos = principales(db, (ref for ref in refs.values() if ref is not None))
    return {
        r.id: {
            "esfuerzo_horas": r.esfuerzo_horas,
            "principal": conocidos.get(refs[r.id]) if refs[r.id] else None,
            "seguidores": conteos.get(r.id, 0),
        }
        for r in registros
    }


def sumar_esfuerzo(registros: Iterable[Registro]) -> Sumas:
    total = pendiente = 0.0
    resueltos = {final for final, _campos in FINALES.values()}
    for registro in registros:
        if referencia(registro) is not None or registro.esfuerzo_horas is None:
            continue
        total += registro.esfuerzo_horas
        if registro.estado not in resueltos:
            pendiente += registro.esfuerzo_horas
    return Sumas(total=total, pendiente=pendiente)
