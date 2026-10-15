import asyncio
import secrets
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import delete, or_, select, update
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from app.core import oidc
from app.core.config import settings
from app.core.security import duracion_sesion
from app.core.time import como_utc, utcnow
from app.models.usuario import Sesion, Usuario
from app.services.usuarios_locales import UsuarioDePrueba

RECHAZOS_DEFINITIVOS = frozenset({"invalid_grant", "invalid_client", "unauthorized_client"})
RECLAMO = timedelta(seconds=30)
ESPERA = timedelta(seconds=10)
PAUSA = 0.2


def _no_autenticado(detalle: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detalle)


def _registrar(db: Session, sub: str | None, email: str, nombre: str) -> Usuario:
    usuario = db.scalar(select(Usuario).where(Usuario.sub_oidc == sub)) if sub else None
    if usuario is None:
        usuario = db.scalar(select(Usuario).where(Usuario.email == email))
    if usuario is None:
        usuario = Usuario(sub_oidc=sub, email=email, nombre=nombre)
        db.add(usuario)
    else:
        usuario.nombre = nombre
        usuario.sub_oidc = sub or usuario.sub_oidc
        choca = db.scalar(select(Usuario).where(Usuario.email == email, Usuario.id != usuario.id))
        if choca is None:
            usuario.email = email
    usuario.ultimo_acceso = utcnow()
    db.flush()
    return usuario


def resolver_usuario(db: Session, claims: dict) -> Usuario:
    sub = claims.get("sub")
    email = claims.get("email")
    if not sub or not email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El inicio de sesión no entregó identificador y correo",
        )
    return _registrar(db, sub, email, claims.get("name") or email)


def resolver_usuario_local(db: Session, prueba: UsuarioDePrueba) -> Usuario:
    return _registrar(db, None, prueba.email, prueba.nombre)


def crear(
    db: Session, usuario: Usuario, tokens: dict, permisos_locales: list[str] | None = None
) -> Sesion:
    db.execute(delete(Sesion).where(Sesion.created_at < utcnow() - duracion_sesion()))
    sesion = Sesion(
        id=secrets.token_urlsafe(32),
        usuario_id=usuario.id,
        access_token=tokens["access_token"],
        refresh_token=tokens.get("refresh_token"),
        access_expira=oidc.vencimiento(tokens.get("expires_in")),
        permisos_locales=permisos_locales,
    )
    db.add(sesion)
    db.commit()
    return sesion


def _vencida(momento: datetime | None, limite: datetime) -> bool:
    momento = como_utc(momento)
    return momento is None or momento <= limite


async def vigente(db: Session, sesion_id: str | None) -> Sesion:
    if not sesion_id:
        raise _no_autenticado("No autenticado")
    sesion = db.get(Sesion, sesion_id)
    if sesion is None:
        raise _no_autenticado("Sesión inválida")
    if _vencida(sesion.created_at, utcnow() - duracion_sesion()):
        cerrar(db, sesion)
        raise _no_autenticado("Sesión expirada")
    if sesion.permisos_locales is not None:
        if not settings.auth_local:
            cerrar(db, sesion)
            raise _no_autenticado("Sesión inválida")
        return sesion
    if _vencida(sesion.access_expira, utcnow()):
        return await _refrescar(db, sesion)
    return sesion


def _rechazo_definitivo(error: oidc.ErrorOIDC) -> bool:
    if error.error in RECHAZOS_DEFINITIVOS:
        return True
    return error.status_code is not None and 400 <= error.status_code < 500


def _releer(db: Session, sesion_id: str) -> Sesion:
    db.expire_all()
    sesion = db.get(Sesion, sesion_id)
    if sesion is None:
        raise _no_autenticado("Sesión expirada")
    return sesion


def _reclamar(db: Session, sesion_id: str) -> bool:
    ahora = utcnow()
    resultado = db.execute(
        update(Sesion)
        .where(
            Sesion.id == sesion_id,
            or_(Sesion.renovando_hasta.is_(None), Sesion.renovando_hasta < ahora),
        )
        .values(renovando_hasta=ahora + RECLAMO)
        .execution_options(synchronize_session=False)
    )
    db.commit()
    return resultado.rowcount == 1


def _soltar(db: Session, sesion_id: str) -> None:
    db.execute(
        update(Sesion)
        .where(Sesion.id == sesion_id)
        .values(renovando_hasta=None)
        .execution_options(synchronize_session=False)
    )
    db.commit()


async def _esperar(db: Session, sesion_id: str) -> Sesion | None:
    limite = utcnow() + ESPERA
    while utcnow() < limite:
        await asyncio.sleep(PAUSA)
        sesion = _releer(db, sesion_id)
        if not _vencida(sesion.access_expira, utcnow()):
            return sesion
        if _vencida(sesion.renovando_hasta, utcnow()):
            return None
    raise _no_disponible()


def _no_disponible() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="No se pudo renovar la sesión; intenta de nuevo en un momento",
    )


async def _refrescar(db: Session, sesion: Sesion) -> Sesion:
    for _ in range(2):
        sesion = _releer(db, sesion.id)
        if not _vencida(sesion.access_expira, utcnow()):
            return sesion
        if not sesion.refresh_token:
            cerrar(db, sesion)
            raise _no_autenticado("Sesión expirada")
        if _reclamar(db, sesion.id):
            return await _renovar(db, sesion.id)
        renovada = await _esperar(db, sesion.id)
        if renovada is not None:
            return renovada
    raise _no_disponible()


async def _renovar(db: Session, sesion_id: str) -> Sesion:
    sesion = _releer(db, sesion_id)
    usado = sesion.refresh_token
    try:
        tokens = await oidc.refrescar(usado)
    except oidc.ErrorOIDC as error:
        sesion = _releer(db, sesion_id)
        if _rechazo_definitivo(error) and sesion.refresh_token == usado:
            cerrar(db, sesion)
            raise _no_autenticado("Sesión expirada") from None
        _soltar(db, sesion_id)
        raise _no_disponible() from None
    sesion = _releer(db, sesion_id)
    sesion.access_token = tokens["access_token"]
    sesion.refresh_token = tokens.get("refresh_token", usado)
    sesion.access_expira = oidc.vencimiento(tokens.get("expires_in"))
    sesion.renovando_hasta = None
    try:
        db.commit()
    except StaleDataError:
        db.rollback()
        raise _no_autenticado("Sesión expirada") from None
    return sesion


def cerrar(db: Session, sesion: Sesion) -> None:
    db.delete(sesion)
    db.commit()
