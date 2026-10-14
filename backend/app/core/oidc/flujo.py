import base64
import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib.parse import urlencode

import httpx

from app.core.config import settings
from app.core.oidc import descubrimiento, http
from app.core.oidc.errores import ErrorOIDC
from app.core.time import utcnow

VIDA_POR_OMISION = 900


@dataclass(frozen=True)
class SolicitudDeAutorizacion:
    url: str
    state: str
    code_verifier: str


def _desafio(verificador: str) -> str:
    resumen = hashlib.sha256(verificador.encode("ascii")).digest()
    return base64.urlsafe_b64encode(resumen).rstrip(b"=").decode("ascii")


async def solicitud_de_autorizacion() -> SolicitudDeAutorizacion:
    descubierto = await descubrimiento.endpoints()
    estado = secrets.token_urlsafe(24)
    verificador = secrets.token_urlsafe(48)
    parametros = {
        "client_id": settings.oidc_client_id,
        "redirect_uri": settings.oidc_redirect_uri,
        "response_type": "code",
        "scope": settings.oidc_scope,
        "state": estado,
        "code_challenge": _desafio(verificador),
        "code_challenge_method": "S256",
    }
    separador = "&" if "?" in descubierto.autorizacion else "?"
    return SolicitudDeAutorizacion(
        url=f"{descubierto.autorizacion}{separador}{urlencode(parametros)}",
        state=estado,
        code_verifier=verificador,
    )


def _credenciales() -> dict[str, str]:
    return {"client_id": settings.oidc_client_id, "client_secret": settings.oidc_client_secret}


async def _post(url: str, datos: dict[str, str]) -> dict:
    cuerpo = {clave: valor for clave, valor in datos.items() if valor}
    try:
        async with http.cliente_http() as cliente:
            respuesta = await cliente.post(url, data=cuerpo)
    except httpx.HTTPError as error:
        raise ErrorOIDC("connection_error", f"No se pudo conectar: {error}") from error
    try:
        leido = respuesta.json()
    except ValueError:
        leido = {}
    if not isinstance(leido, dict):
        leido = {}
    if respuesta.is_success:
        return leido
    raise ErrorOIDC(
        str(leido.get("error") or "oidc_error"),
        str(
            leido.get("error_description")
            or leido.get("detail")
            or f"El proveedor respondió HTTP {respuesta.status_code}"
        ),
        respuesta.status_code,
    )


async def _tokens(datos: dict[str, str]) -> dict:
    descubierto = await descubrimiento.endpoints()
    tokens = await _post(descubierto.token, {**datos, **_credenciales()})
    if not isinstance(tokens.get("access_token"), str) or not tokens["access_token"]:
        raise ErrorOIDC("respuesta_invalida", "La respuesta de tokens no trae access_token")
    return tokens


async def canjear_codigo(codigo: str, verificador: str) -> dict:
    return await _tokens(
        {
            "grant_type": "authorization_code",
            "code": codigo,
            "redirect_uri": settings.oidc_redirect_uri,
            "code_verifier": verificador,
        }
    )


async def refrescar(refresh_token: str) -> dict:
    return await _tokens({"grant_type": "refresh_token", "refresh_token": refresh_token})


async def revocar(refresh_token: str) -> None:
    try:
        descubierto = await descubrimiento.endpoints()
        if descubierto.revocacion is None:
            return
        await _post(descubierto.revocacion, {**_credenciales(), "token": refresh_token})
    except ErrorOIDC:
        return


def vencimiento(expires_in: object) -> datetime:
    valido = isinstance(expires_in, int) and not isinstance(expires_in, bool) and expires_in > 0
    segundos = expires_in if valido else VIDA_POR_OMISION
    return utcnow() + timedelta(seconds=segundos)


def url_de_salida() -> str:
    return f"{settings.frontend_url}/"
