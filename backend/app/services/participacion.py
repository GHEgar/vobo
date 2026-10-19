import hashlib
import hmac
from collections import Counter, defaultdict
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.time import utcnow
from app.models.falla import Falla
from app.models.presencia import Presencia
from app.models.proyecto import Proyecto
from app.models.resultado import Resultado
from app.models.ronda import Ronda
from app.models.usuario import Usuario
from app.schemas.participacion import (
    Detalle,
    EnlaceGrafo,
    Estado,
    Participacion,
    PersonaGrafo,
    ProyectoGrafo,
)
from app.services import contenido
from app.services import proyectos as servicio_proyectos
from app.services.consolidado import por_caso, resultados_de_ronda
from app.services.presencia import ACTIVO

ESTADOS = (
    Estado(key="pasa", label="Pasa", tone="good"),
    Estado(key="falla", label="Falla", tone="critical"),
    Estado(key="no_pude", label="No pude", tone="warning"),
    Estado(key="pendiente", label="Pendiente", tone="neutral"),
)


@dataclass
class Fuente:
    proyecto: Proyecto
    ronda: Ronda | None
    resultados: list[Resultado]


def id_de_persona(email: str) -> str:
    clave = settings.secret_key.encode()
    resumen = hmac.new(clave, f"participacion:{email.lower()}".encode(), hashlib.sha256)
    return resumen.hexdigest()[:16]


def _ronda_de(db: Session, proyecto: Proyecto, ronda_id: int | None) -> Ronda | None:
    consulta = select(Ronda).where(Ronda.proyecto_id == proyecto.id)
    if ronda_id is not None:
        return db.scalar(consulta.where(Ronda.id == ronda_id))
    orden = (Ronda.abierta.desc(), Ronda.creada.desc(), Ronda.id.desc())
    return db.scalar(consulta.order_by(*orden).limit(1))


def fuentes(db: Session, claves: list[str], ronda_id: int | None) -> list[Fuente]:
    todos = servicio_proyectos.ordenados(db, con_archivados=bool(claves))
    elegidos = [p for p in todos if p.clave in claves] if claves else todos
    salida = []
    for proyecto in elegidos:
        ronda = _ronda_de(db, proyecto, ronda_id if len(elegidos) == 1 else None)
        resultados = resultados_de_ronda(db, ronda.id) if ronda else []
        salida.append(Fuente(proyecto, ronda, resultados))
    return salida


def _fallas_abiertas(db: Session, ronda: Ronda | None) -> int:
    if ronda is None:
        return 0
    consulta = select(func.count(Falla.id)).where(
        Falla.ronda_id == ronda.id, Falla.tipo != "no_pude", Falla.estado != "cerrada"
    )
    return int(db.scalar(consulta) or 0)


def _proyecto(db: Session, fuente: Fuente) -> ProyectoGrafo:
    estados = por_caso(contenido.obtener(fuente.proyecto), fuente.resultados)
    cuenta = Counter(estados.values())
    total = len(estados)
    detalles = []
    if fuente.ronda is not None:
        detalles.append(Detalle(label="Ronda", value=fuente.ronda.nombre))
        if fuente.ronda.snapshot:
            detalles.append(Detalle(label="Versión", value=fuente.ronda.snapshot))
    detalles.append(Detalle(label="Fallas abiertas", value=_fallas_abiertas(db, fuente.ronda)))
    return ProyectoGrafo(
        id=fuente.proyecto.clave,
        name=fuente.proyecto.nombre,
        description=fuente.proyecto.descripcion or None,
        color=fuente.proyecto.color_nombre or None,
        progress=round((total - cuenta["pendiente"]) / total, 4) if total else 0.0,
        counts={e.key: cuenta[e.key] for e in ESTADOS if cuenta[e.key]},
        details=detalles,
    )


def _activos(db: Session, proyecto_ids: list[int]) -> set[str]:
    consulta = select(Presencia.usuario_email).where(
        Presencia.actualizado >= utcnow() - ACTIVO, Presencia.proyecto_id.in_(proyecto_ids)
    )
    return set(db.scalars(consulta))


def _fallas_por_persona(db: Session, rondas: list[int]) -> Counter[str]:
    if not rondas:
        return Counter()
    consulta = select(Falla.usuario_email).where(Falla.ronda_id.in_(rondas))
    return Counter(db.scalars(consulta))


def _marcados(lista: list[Fuente]) -> dict[str, dict[str, int]]:
    marcados: dict[str, dict[str, int]] = defaultdict(dict)
    for fuente in lista:
        propios = Counter(r.usuario_email for r in fuente.resultados if r.estado != "pendiente")
        for email, n in propios.items():
            marcados[email][fuente.proyecto.clave] = n
    return marcados


def calcular(db: Session, claves: list[str], ronda_id: int | None = None) -> Participacion:
    lista = fuentes(db, claves, ronda_id)
    marcados = _marcados(lista)
    nombres = {
        u.email: u.nombre for u in db.scalars(select(Usuario).where(Usuario.email.in_(marcados)))
    }
    activos = _activos(db, [f.proyecto.id for f in lista])
    fallas = _fallas_por_persona(db, [f.ronda.id for f in lista if f.ronda])

    def orden(email: str) -> str:
        return (nombres.get(email) or email).lower()

    personas = [
        PersonaGrafo(
            id=id_de_persona(email),
            name=nombres.get(email) or email.split("@")[0],
            metric=sum(por_proyecto.values()),
            active=email in activos,
            details=[Detalle(label="Fallas reportadas", value=fallas[email])],
        )
        for email, por_proyecto in sorted(marcados.items(), key=lambda par: orden(par[0]))
    ]
    enlaces = [
        EnlaceGrafo(person=id_de_persona(email), project=clave, weight=n)
        for email, por_proyecto in marcados.items()
        for clave, n in por_proyecto.items()
    ]
    return Participacion(
        statuses=list(ESTADOS),
        projects=[_proyecto(db, f) for f in lista],
        people=personas,
        links=enlaces,
    )
