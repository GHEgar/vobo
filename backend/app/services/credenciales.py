import hashlib
import secrets
from functools import cache

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import HTTPException, status

MINIMO = 10
MAXIMO = 256
BYTES_TOKEN = 32

COMUNES = frozenset(
    {
        "123456",
        "123456789",
        "12345678",
        "password",
        "qwerty",
        "12345",
        "1234567",
        "111111",
        "123123",
        "abc123",
        "1234567890",
        "password1",
        "000000",
        "iloveyou",
        "qwerty123",
        "qwertyuiop",
        "1q2w3e4r5t",
        "contraseña",
        "contrasena",
        "password123",
    }
)

_hasher = PasswordHasher()


@cache
def _senuelo() -> str:
    return _hasher.hash(secrets.token_urlsafe(16))


def _rechazo(detalle: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=detalle)


def validar(contrasena: str) -> None:
    if len(contrasena) < MINIMO:
        raise _rechazo(f"La contraseña debe tener al menos {MINIMO} caracteres")
    if len(contrasena) > MAXIMO:
        raise _rechazo(f"La contraseña no puede pasar de {MAXIMO} caracteres")
    if contrasena.strip().lower() in COMUNES:
        raise _rechazo("Esa contraseña es demasiado común; elige otra")


def hashear(contrasena: str) -> str:
    return _hasher.hash(contrasena)


def verificar(guardado: str | None, contrasena: str) -> bool:
    try:
        return _hasher.verify(guardado or _senuelo(), contrasena[:MAXIMO]) and bool(guardado)
    except (VerificationError, InvalidHashError):
        return False


def necesita_rehash(guardado: str) -> bool:
    return _hasher.check_needs_rehash(guardado)


def hash_de_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def nuevo_token() -> tuple[str, str]:
    token = secrets.token_urlsafe(BYTES_TOKEN)
    return token, hash_de_token(token)
