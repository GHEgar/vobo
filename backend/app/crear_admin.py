import argparse
import sys

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.usuario import Usuario
from app.schemas.admin import InvitacionCrear
from app.services import cuentas_propias, roles

AUTOR = "consola"


class PrimerAdminImposible(RuntimeError):
    pass


def _sin_administradores(db: Session) -> None:
    if roles.administradores(db) > 0:
        raise PrimerAdminImposible(
            "Ya hay una persona con Administración; asigna el resto desde Administración"
        )


def invitacion_inicial(db: Session, email: str) -> str:
    if not settings.auth_cuentas:
        raise PrimerAdminImposible("AUTH_MODO debe ser cuentas o ambos para crear cuentas propias")
    _sin_administradores(db)
    correo = InvitacionCrear(email=email).email
    try:
        _invitacion, enlace = cuentas_propias.invitar(db, correo, [roles.CLAVE_ADMIN], AUTOR)
    except HTTPException as error:
        raise PrimerAdminImposible(str(error.detail)) from None
    return enlace


def asignar_inicial(db: Session, email: str) -> str:
    if not settings.auth_oidc:
        raise PrimerAdminImposible(
            "AUTH_MODO debe ser oidc para asignar el rol a una persona existente"
        )
    _sin_administradores(db)
    correo = InvitacionCrear(email=email).email
    usuario = db.scalar(select(Usuario).where(func.lower(Usuario.email) == correo.lower()))
    if usuario is None:
        raise PrimerAdminImposible(
            f"{correo} todavía no ha entrado; que inicie sesión una vez con su cuenta y repite"
        )
    asignado = usuario.email
    roles.agregar(db, usuario, [roles.CLAVE_ADMIN])
    db.commit()
    return asignado


def main(argumentos: list[str] | None = None) -> int:
    lector = argparse.ArgumentParser(
        prog="python -m app.crear_admin",
        description="Primera persona con Administración: invitación o rol a quien ya entró",
    )
    lector.add_argument("email")
    leidos = lector.parse_args(argumentos)
    try:
        with SessionLocal() as db:
            if settings.auth_cuentas:
                enlace = invitacion_inicial(db, leidos.email)
            else:
                asignado = asignar_inicial(db, leidos.email)
    except (PrimerAdminImposible, ValueError) as error:
        print(f"crear_admin: {error}", file=sys.stderr)
        return 1
    if settings.auth_cuentas:
        print(f"Invitación de administración para {leidos.email} (vale 48 h, un solo uso):")
        print(enlace)
    else:
        print(f"Administración asignada a {asignado}; recarga la app para verla")
    return 0


if __name__ == "__main__":
    sys.exit(main())
