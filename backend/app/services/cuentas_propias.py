from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.time import como_utc, utcnow
from app.models.cuenta import Cuenta, Invitacion, Restablecimiento
from app.models.usuario import Sesion, Usuario
from app.services import credenciales, roles

VIGENCIA = timedelta(hours=48)
ORIGEN = "cuenta"


def _no_valido() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="El enlace no es válido o ya expiró"
    )


def enlace(ruta: str, token: str) -> str:
    return f"{settings.frontend_url}/{ruta}/{token}"


def por_correo(db: Session, email: str) -> Usuario | None:
    return db.scalar(select(Usuario).where(func.lower(Usuario.email) == email.strip().lower()))


def cuenta_de(db: Session, usuario_id: int) -> Cuenta | None:
    return db.get(Cuenta, usuario_id)


def cerrar_sesiones(db: Session, usuario_id: int, excepto: str | None = None) -> None:
    consulta = delete(Sesion).where(Sesion.usuario_id == usuario_id, Sesion.origen == ORIGEN)
    if excepto:
        consulta = consulta.where(Sesion.id != excepto)
    db.execute(consulta)


def _fijar_contrasena(db: Session, usuario: Usuario, contrasena: str) -> Cuenta:
    credenciales.validar(contrasena)
    cuenta = cuenta_de(db, usuario.id)
    ahora = utcnow()
    if cuenta is None:
        cuenta = Cuenta(usuario_id=usuario.id, creada=ahora, activa=True)
        db.add(cuenta)
    cuenta.hash = credenciales.hashear(contrasena)
    cuenta.ultimo_cambio = ahora
    cuenta.debe_cambiar = False
    return cuenta


def invitar(db: Session, email: str, claves: list[str], autor: str) -> tuple[Invitacion, str]:
    roles.por_claves(db, claves)
    existente = por_correo(db, email)
    if existente is not None and cuenta_de(db, existente.id) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esa persona ya tiene cuenta; usa «Restablecer contraseña»",
        )
    token, resumen = credenciales.nuevo_token()
    invitacion = Invitacion(
        token_hash=resumen,
        email=email,
        roles=sorted(set(claves)),
        creada_por=autor,
        expira=utcnow() + VIGENCIA,
    )
    db.add(invitacion)
    db.commit()
    return invitacion, enlace("invitacion", token)


def invitacion_vigente(db: Session, token: str) -> Invitacion:
    invitacion = db.scalar(
        select(Invitacion).where(Invitacion.token_hash == credenciales.hash_de_token(token))
    )
    if invitacion is None or invitacion.usada or como_utc(invitacion.expira) <= utcnow():
        raise _no_valido()
    return invitacion


def aceptar_invitacion(db: Session, token: str, nombre: str, contrasena: str) -> Usuario:
    invitacion = invitacion_vigente(db, token)
    credenciales.validar(contrasena)
    usuario = por_correo(db, invitacion.email)
    if usuario is None:
        usuario = Usuario(email=invitacion.email, nombre=nombre.strip())
        db.add(usuario)
        db.flush()
    else:
        usuario.nombre = nombre.strip()
    _fijar_contrasena(db, usuario, contrasena)
    roles.agregar(db, usuario, list(invitacion.roles or []))
    invitacion.usada = utcnow()
    usuario.ultimo_acceso = utcnow()
    db.commit()
    return usuario


def pendientes(db: Session) -> list[Invitacion]:
    return list(
        db.scalars(
            select(Invitacion)
            .where(Invitacion.usada.is_(None), Invitacion.expira > utcnow())
            .order_by(Invitacion.creada.desc())
        )
    )


def revocar_invitacion(db: Session, invitacion_id: int) -> None:
    invitacion = db.get(Invitacion, invitacion_id)
    if invitacion is None or invitacion.usada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invitación no encontrada"
        )
    invitacion.usada = utcnow()
    db.commit()


def restablecimiento(db: Session, usuario: Usuario, autor: str) -> tuple[Restablecimiento, str]:
    ahora = utcnow()
    db.execute(
        update(Restablecimiento)
        .where(Restablecimiento.usuario_id == usuario.id, Restablecimiento.usado.is_(None))
        .values(usado=ahora)
    )
    token, resumen = credenciales.nuevo_token()
    nuevo = Restablecimiento(
        token_hash=resumen, usuario_id=usuario.id, creado_por=autor, expira=ahora + VIGENCIA
    )
    db.add(nuevo)
    db.commit()
    return nuevo, enlace("restablecer", token)


def restablecimiento_vigente(db: Session, token: str) -> Restablecimiento:
    encontrado = db.scalar(
        select(Restablecimiento).where(
            Restablecimiento.token_hash == credenciales.hash_de_token(token)
        )
    )
    if encontrado is None or encontrado.usado or como_utc(encontrado.expira) <= utcnow():
        raise _no_valido()
    return encontrado


def restablecer(db: Session, token: str, contrasena: str) -> tuple[Usuario, Cuenta]:
    encontrado = restablecimiento_vigente(db, token)
    usuario = db.get(Usuario, encontrado.usuario_id)
    if usuario is None:
        raise _no_valido()
    cuenta = _fijar_contrasena(db, usuario, contrasena)
    encontrado.usado = utcnow()
    cerrar_sesiones(db, usuario.id)
    db.commit()
    return usuario, cuenta


def autenticar(db: Session, email: str, contrasena: str) -> Usuario | None:
    usuario = por_correo(db, email)
    cuenta = cuenta_de(db, usuario.id) if usuario else None
    if not credenciales.verificar(cuenta.hash if cuenta else None, contrasena):
        return None
    if not cuenta.activa:
        return None
    if credenciales.necesita_rehash(cuenta.hash):
        cuenta.hash = credenciales.hashear(contrasena)
    usuario.ultimo_acceso = utcnow()
    db.commit()
    return usuario


def cambiar(db: Session, usuario: Usuario, actual: str, nueva: str, sesion_id: str | None) -> None:
    cuenta = cuenta_de(db, usuario.id)
    if cuenta is None or not credenciales.verificar(cuenta.hash, actual):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña actual no es correcta"
        )
    _fijar_contrasena(db, usuario, nueva)
    cerrar_sesiones(db, usuario.id, excepto=sesion_id)
    db.commit()


def fijar_activa(db: Session, usuario: Usuario, activa: bool) -> Cuenta:
    cuenta = cuenta_de(db, usuario.id)
    if cuenta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Esta persona no tiene cuenta propia"
        )
    cuenta.activa = activa
    if not activa:
        cerrar_sesiones(db, usuario.id)
    db.commit()
    return cuenta
