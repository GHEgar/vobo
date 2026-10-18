from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.time import como_utc, utcnow
from app.models.pantalla import Pantalla
from app.models.proyecto import Proyecto
from app.schemas.pantalla import PantallaCambios, PantallaCrear
from app.services import credenciales

RUTA = "pantalla"
USO_MINIMO = timedelta(minutes=1)


def _no_encontrada() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pantalla no encontrada")


def enlace(token: str) -> str:
    return f"{settings.frontend_url}/{RUTA}/{token}"


def _validar_proyectos(db: Session, claves: list[str]) -> None:
    if not claves:
        return
    existentes = set(db.scalars(select(Proyecto.clave).where(Proyecto.clave.in_(claves))))
    faltan = [c for c in claves if c not in existentes]
    if faltan:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Proyecto desconocido: {', '.join(faltan)}",
        )


def listar(db: Session) -> list[Pantalla]:
    return list(db.scalars(select(Pantalla).order_by(Pantalla.creada, Pantalla.id)))


def obtener_o_404(db: Session, pantalla_id: int) -> Pantalla:
    pantalla = db.get(Pantalla, pantalla_id)
    if pantalla is None:
        raise _no_encontrada()
    return pantalla


def crear(db: Session, datos: PantallaCrear, autor: str) -> tuple[Pantalla, str]:
    _validar_proyectos(db, datos.proyectos)
    token, resumen = credenciales.nuevo_token()
    pantalla = Pantalla(
        nombre=datos.nombre,
        token_hash=resumen,
        vistas=list(datos.vistas),
        segundos=datos.segundos,
        proyectos=list(datos.proyectos),
        activa=True,
        autor_email=autor,
    )
    db.add(pantalla)
    db.commit()
    db.refresh(pantalla)
    return pantalla, enlace(token)


def actualizar(db: Session, pantalla: Pantalla, cambios: PantallaCambios) -> Pantalla:
    valores = cambios.model_dump(exclude_none=True)
    if "proyectos" in valores:
        _validar_proyectos(db, valores["proyectos"])
    for campo, valor in valores.items():
        setattr(pantalla, campo, list(valor) if isinstance(valor, list) else valor)
    db.commit()
    db.refresh(pantalla)
    return pantalla


def regenerar(db: Session, pantalla: Pantalla) -> tuple[Pantalla, str]:
    token, resumen = credenciales.nuevo_token()
    pantalla.token_hash = resumen
    db.commit()
    db.refresh(pantalla)
    return pantalla, enlace(token)


def borrar(db: Session, pantalla: Pantalla) -> None:
    db.delete(pantalla)
    db.commit()


def vigente(db: Session, token: str) -> Pantalla:
    if not token or len(token) > 200:
        raise _no_encontrada()
    pantalla = db.scalar(
        select(Pantalla).where(Pantalla.token_hash == credenciales.hash_de_token(token))
    )
    if pantalla is None or not pantalla.activa:
        raise _no_encontrada()
    return pantalla


def registrar_uso(db: Session, pantalla: Pantalla) -> None:
    ahora = utcnow()
    anterior = como_utc(pantalla.ultimo_uso)
    if anterior is not None and ahora - anterior < USO_MINIMO:
        return
    pantalla.ultimo_uso = ahora
    db.commit()
