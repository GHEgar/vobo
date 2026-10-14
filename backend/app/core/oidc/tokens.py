import time

import httpx
from fastapi import HTTPException, status
from jose import JWTError, jwt

from app.core.config import settings
from app.core.oidc import descubrimiento, http
from app.core.oidc.errores import ErrorOIDC

ALGORITMO = "RS256"
VIDA_JWKS = 3600
ESPERA_REFRESCO_JWKS = 30

_jwks: dict[str, object] = {"exp": 0.0, "jwks": None, "retry_after": 0.0}


def _no_autorizado(detalle: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detalle)


def _tiene_kid(jwks: dict, kid: str) -> bool:
    return any(llave.get("kid") == kid for llave in jwks.get("keys", []))


async def _obtener_jwks(url: str, kid: str | None) -> dict:
    ahora = time.time()
    guardado = _jwks["jwks"]
    if isinstance(guardado, dict) and float(_jwks["exp"]) > ahora:
        if kid is None or _tiene_kid(guardado, kid):
            return guardado
        if ahora < float(_jwks["retry_after"]):
            return guardado
        _jwks["retry_after"] = ahora + ESPERA_REFRESCO_JWKS
    async with http.cliente_http() as cliente:
        respuesta = await cliente.get(url)
        respuesta.raise_for_status()
    nuevo = respuesta.json()
    _jwks["jwks"] = nuevo
    _jwks["exp"] = ahora + VIDA_JWKS
    return nuevo


async def validar_access_token(token: str) -> dict:
    try:
        cabecera = jwt.get_unverified_header(token)
    except JWTError as error:
        raise _no_autorizado(f"Token inválido: {error}") from None
    algoritmo = cabecera.get("alg")
    if algoritmo != ALGORITMO:
        raise _no_autorizado(f"Algoritmo de token no soportado: {algoritmo}")
    if not settings.oidc_audience:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OIDC_AUDIENCE no configurada",
        )
    try:
        descubierto = await descubrimiento.endpoints()
        jwks = await _obtener_jwks(descubierto.jwks, cabecera.get("kid"))
        claims = jwt.decode(
            token,
            jwks,
            algorithms=[ALGORITMO],
            audience=settings.oidc_audience,
            options={"verify_aud": True},
        )
    except JWTError as error:
        raise _no_autorizado(f"Token inválido: {error}") from None
    except (httpx.HTTPError, ValueError, ErrorOIDC):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No se pudieron obtener las llaves para validar la sesión",
        ) from None
    if str(claims.get("iss", "")).rstrip("/") != descubrimiento.issuer_esperado(descubierto):
        raise _no_autorizado("Issuer inválido")
    if settings.oidc_token_typ and claims.get("typ") != settings.oidc_token_typ:
        raise _no_autorizado("Tipo de token no válido")
    return claims


def olvidar() -> None:
    _jwks["jwks"] = None
    _jwks["exp"] = 0.0
    _jwks["retry_after"] = 0.0
