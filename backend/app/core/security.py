import base64
import hashlib
import hmac
import json
from datetime import timedelta
from urllib.parse import urlsplit

from fastapi import HTTPException, Request, Response, status

from app.core.config import settings

COOKIE_SESION = "validacion_sesion"
COOKIE_TRANSACCION = "validacion_oidc"
COOKIE_PATH = "/api"
PATH_TRANSACCION = "/api/auth"
CABECERA_CSRF = "X-CSRF-Token"
METODOS_SEGUROS = frozenset({"GET", "HEAD", "OPTIONS"})
VIDA_TRANSACCION = 600


def duracion_sesion() -> timedelta:
    return timedelta(minutes=settings.sesion_minutos)


def csrf_de(sesion_id: str) -> str:
    firma = hmac.new(settings.secret_key.encode(), f"csrf:{sesion_id}".encode(), hashlib.sha256)
    return firma.hexdigest()


def emitir_cookie(response: Response, sesion_id: str) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.set_cookie(
        key=COOKIE_SESION,
        value=sesion_id,
        max_age=int(duracion_sesion().total_seconds()),
        path=COOKIE_PATH,
        secure=settings.session_cookie_secure,
        httponly=True,
        samesite="strict",
    )


def borrar_cookie(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.delete_cookie(
        key=COOKIE_SESION,
        path=COOKIE_PATH,
        secure=settings.session_cookie_secure,
        httponly=True,
        samesite="strict",
    )


def guardar_transaccion(response: Response, datos: dict[str, str]) -> None:
    valor = base64.urlsafe_b64encode(json.dumps(datos).encode()).decode("ascii")
    response.set_cookie(
        key=COOKIE_TRANSACCION,
        value=valor,
        max_age=VIDA_TRANSACCION,
        path=PATH_TRANSACCION,
        secure=settings.session_cookie_secure,
        httponly=True,
        samesite="lax",
    )


def leer_transaccion(request: Request) -> dict[str, str] | None:
    valor = request.cookies.get(COOKIE_TRANSACCION)
    if not valor:
        return None
    try:
        datos = json.loads(base64.urlsafe_b64decode(valor.encode("ascii")))
    except (ValueError, UnicodeDecodeError):
        return None
    return datos if isinstance(datos, dict) else None


def borrar_transaccion(response: Response) -> None:
    response.delete_cookie(key=COOKIE_TRANSACCION, path=PATH_TRANSACCION)


def verificar_origen(request: Request) -> None:
    origen = request.headers.get("origin")
    if origen is None or origen in settings.origenes_permitidos:
        return
    if urlsplit(origen).netloc == request.headers.get("host"):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Origen no permitido")


def verificar_csrf(request: Request, sesion_id: str) -> None:
    if request.method in METODOS_SEGUROS:
        return
    verificar_origen(request)
    enviado = request.headers.get(CABECERA_CSRF, "")
    if not hmac.compare_digest(enviado, csrf_de(sesion_id)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token CSRF inválido")
