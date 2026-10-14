import time
from dataclasses import dataclass

import httpx

from app.core.config import settings
from app.core.oidc import http
from app.core.oidc.errores import ErrorOIDC

RUTA_DESCUBRIMIENTO = "/.well-known/openid-configuration"
VIDA_DESCUBRIMIENTO = 3600
OBLIGATORIOS = ("issuer", "authorization_endpoint", "token_endpoint", "jwks_uri")


@dataclass(frozen=True)
class Endpoints:
    issuer: str
    autorizacion: str
    token: str
    jwks: str
    revocacion: str | None


_cache: dict[str, object] = {"exp": 0.0, "endpoints": None}


def _base(url: str) -> str:
    return url.rstrip("/")


def interna(url: str) -> str:
    publica = _base(settings.oidc_publico)
    issuer = _base(settings.oidc_issuer_url)
    if publica and publica != issuer and _con_prefijo(url, publica):
        return issuer + url[len(publica) :]
    return url


def publica(url: str) -> str:
    destino = _base(settings.oidc_publico)
    issuer = _base(settings.oidc_issuer_url)
    if destino and destino != issuer and _con_prefijo(url, issuer):
        return destino + url[len(issuer) :]
    return url


def _con_prefijo(url: str, prefijo: str) -> bool:
    return url == prefijo or url.startswith(prefijo + "/") or url.startswith(prefijo + "?")


def _desde(datos: object) -> Endpoints:
    if not isinstance(datos, dict):
        raise ErrorOIDC("discovery_invalido", "La configuración del proveedor no es un objeto")
    faltan = [campo for campo in OBLIGATORIOS if not isinstance(datos.get(campo), str)]
    if faltan:
        raise ErrorOIDC(
            "discovery_invalido", f"A la configuración del proveedor le falta {', '.join(faltan)}"
        )
    revocacion = datos.get("revocation_endpoint")
    return Endpoints(
        issuer=datos["issuer"],
        autorizacion=publica(datos["authorization_endpoint"]),
        token=interna(datos["token_endpoint"]),
        jwks=interna(datos["jwks_uri"]),
        revocacion=interna(revocacion) if isinstance(revocacion, str) and revocacion else None,
    )


async def endpoints() -> Endpoints:
    ahora = time.time()
    guardados = _cache["endpoints"]
    if isinstance(guardados, Endpoints) and float(_cache["exp"]) > ahora:
        return guardados
    url = _base(settings.oidc_issuer_url) + RUTA_DESCUBRIMIENTO
    try:
        async with http.cliente_http() as cliente:
            respuesta = await cliente.get(url)
            respuesta.raise_for_status()
        datos = respuesta.json()
    except (httpx.HTTPError, ValueError) as error:
        raise ErrorOIDC(
            "discovery_no_disponible", f"No se pudo leer la configuración del proveedor: {error}"
        ) from error
    nuevos = _desde(datos)
    _cache["endpoints"] = nuevos
    _cache["exp"] = ahora + VIDA_DESCUBRIMIENTO
    return nuevos


def issuer_esperado(descubierto: Endpoints) -> str:
    return _base(settings.oidc_expected_issuer or descubierto.issuer)


def olvidar() -> None:
    _cache["endpoints"] = None
    _cache["exp"] = 0.0
