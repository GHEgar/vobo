import argparse
import sys

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.schemas.admin import InvitacionCrear
from app.services import cuentas_propias, roles

AUTOR = "consola"


class PrimerAdminImposible(RuntimeError):
    pass


def invitacion_inicial(db: Session, email: str) -> str:
    if not settings.auth_cuentas:
        raise PrimerAdminImposible("AUTH_MODO debe ser cuentas o ambos para crear cuentas propias")
    if roles.administradores(db) > 0:
        raise PrimerAdminImposible(
            "Ya hay una persona con Administración; invita al resto desde Administración"
        )
    correo = InvitacionCrear(email=email).email
    try:
        _invitacion, enlace = cuentas_propias.invitar(db, correo, [roles.CLAVE_ADMIN], AUTOR)
    except HTTPException as error:
        raise PrimerAdminImposible(str(error.detail)) from None
    return enlace


def main(argumentos: list[str] | None = None) -> int:
    lector = argparse.ArgumentParser(
        prog="python -m app.crear_admin",
        description="Crea la invitación de la primera persona con Administración",
    )
    lector.add_argument("email")
    leidos = lector.parse_args(argumentos)
    try:
        with SessionLocal() as db:
            enlace = invitacion_inicial(db, leidos.email)
    except (PrimerAdminImposible, ValueError) as error:
        print(f"crear_admin: {error}", file=sys.stderr)
        return 1
    print(f"Invitación de administración para {leidos.email} (vale 48 h, un solo uso):")
    print(enlace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
