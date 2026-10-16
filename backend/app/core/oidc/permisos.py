import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.oidc import descubrimiento, http
from app.core.oidc.tokens import validar_access_token


def _no_disponibles() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY, detail="No se pudieron consultar los permisos"
    )


def _como_conjunto(valor: object) -> set[str]:
    if isinstance(valor, str):
        return set(valor.split())
    if isinstance(valor, list | tuple | set):
        return {str(v) for v in valor if v is not None}
    return set()


async def _por_url(token: str, url: str) -> set[str]:
    try:
        async with http.cliente_http() as cliente:
            respuesta = await cliente.get(url, headers={"Authorization": f"Bearer {token}"})
            respuesta.raise_for_status()
        datos = respuesta.json()
    except httpx.HTTPStatusError as error:
        if error.response.status_code == status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o revocado"
            ) from None
        raise _no_disponibles() from None
    except (httpx.HTTPError, ValueError):
        raise _no_disponibles() from None
    if not isinstance(datos, dict):
        raise _no_disponibles()
    return _como_conjunto(datos.get("permissions", []))


async def permisos_y_grupos(token: str) -> tuple[set[str], set[str]]:
    claims = await validar_access_token(token)
    grupos = (
        _como_conjunto(claims.get(settings.oidc_roles_claim, []))
        if settings.oidc_roles_claim
        else set()
    )
    if settings.oidc_permisos_url:
        url = descubrimiento.interna(settings.oidc_permisos_url)
        return await _por_url(token, url), grupos
    return _como_conjunto(claims.get(settings.oidc_permisos_claim, [])), grupos


async def permisos_de(token: str) -> set[str]:
    permisos, _grupos = await permisos_y_grupos(token)
    return permisos
