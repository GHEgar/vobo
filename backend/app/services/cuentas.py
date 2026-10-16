import logging
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.schemas.cuenta import CuentaPrueba
from app.schemas.instancia import CuentaDeInstancia
from app.services import configuracion

logger = logging.getLogger("validacion.cuentas")

DESCRIPCION_GENERICA = "Cuenta de prueba"


def _descripciones() -> list[CuentaDeInstancia]:
    try:
        return configuracion.efectiva().cuentas
    except (ValueError, SQLAlchemyError):
        return []


def descripcion_de(email: str, descripciones: list[CuentaDeInstancia] | None = None) -> str:
    local = email.split("@", 1)[0].lower()
    return next(
        (
            c.descripcion
            for c in (_descripciones() if descripciones is None else descripciones)
            if local.startswith(c.prefijo.lower())
        ),
        DESCRIPCION_GENERICA,
    )


def listar(ruta: str | None = None) -> list[CuentaPrueba]:
    archivo = Path(ruta or settings.cuentas_path)
    try:
        lineas = archivo.read_text(encoding="utf-8").splitlines()
    except (FileNotFoundError, PermissionError, IsADirectoryError):
        return []
    descripciones = _descripciones()
    cuentas = []
    for numero, linea in enumerate(lineas, start=1):
        limpia = linea.strip()
        if not limpia or limpia.startswith("#"):
            continue
        email, separador, password = limpia.partition("=")
        if not separador or not email.strip() or not password:
            logger.warning("cuentas de prueba: línea %s sin formato correo=contraseña", numero)
            continue
        email = email.strip()
        cuentas.append(
            CuentaPrueba(
                email=email,
                password=password.strip(),
                descripcion=descripcion_de(email, descripciones),
            )
        )
    return cuentas
