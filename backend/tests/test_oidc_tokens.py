import asyncio

import pytest
from fastapi import HTTPException
from jose import jwt

from app.core import oidc
from app.core.config import settings
from app.core.oidc import tokens
from tests.idp_falso import INTERNA, nueva_llave

JWKS = f"{INTERNA}/.well-known/jwks.json"


def _rechazo(corrutina) -> HTTPException:
    with pytest.raises(HTTPException) as error:
        asyncio.run(corrutina)
    return error.value


def test_token_valido_devuelve_claims(idp) -> None:
    claims = asyncio.run(oidc.validar_access_token(idp.token()))
    assert claims["sub"] == "u-1"
    assert claims["aud"] == "validacion"


@pytest.mark.parametrize(
    ("claims", "detalle"),
    [
        ({"aud": "otra-app"}, "Token inválido"),
        ({"iss": "https://otro.ejemplo"}, "Issuer inválido"),
        ({"typ": "refresh"}, "Tipo de token no válido"),
        ({"typ": None}, "Tipo de token no válido"),
        ({"exp": 1}, "Token inválido"),
    ],
)
def test_rechaza_aud_iss_typ_y_vencido(idp, claims, detalle) -> None:
    error = _rechazo(oidc.validar_access_token(idp.token(**claims)))
    assert error.status_code == 401
    assert error.detail.startswith(detalle)


def test_typ_opcional(idp, monkeypatch) -> None:
    monkeypatch.setattr(settings, "oidc_token_typ", "")
    assert asyncio.run(oidc.validar_access_token(idp.token(typ=None)))["sub"] == "u-1"


def test_issuer_esperado_vacio_usa_el_del_discovery(idp, monkeypatch) -> None:
    monkeypatch.setattr(settings, "oidc_expected_issuer", "")
    assert asyncio.run(oidc.validar_access_token(idp.token()))["sub"] == "u-1"
    idp.descubrimiento = {**idp.descubrimiento, "issuer": "https://otro.ejemplo"}
    oidc.olvidar_caches()
    assert _rechazo(oidc.validar_access_token(idp.token())).detail == "Issuer inválido"


def test_solo_acepta_rs256(idp) -> None:
    falso = jwt.encode({"sub": "u-1", "aud": "validacion"}, "secreto", algorithm="HS256")
    error = _rechazo(oidc.validar_access_token(falso))
    assert error.status_code == 401
    assert "HS256" in error.detail


def test_kid_desconocido_refresca_el_jwks_con_espera(idp) -> None:
    asyncio.run(oidc.validar_access_token(idp.token()))
    asyncio.run(oidc.validar_access_token(idp.token()))
    assert idp.llamadas(JWKS) == 1
    rotada = nueva_llave("k2")
    idp.llaves.append(rotada)
    assert asyncio.run(oidc.validar_access_token(idp.token(rotada)))["sub"] == "u-1"
    assert idp.llamadas(JWKS) == 2
    inventada = nueva_llave("k3")
    assert _rechazo(oidc.validar_access_token(idp.token(inventada))).status_code == 401
    assert _rechazo(oidc.validar_access_token(idp.token(inventada))).status_code == 401
    assert idp.llamadas(JWKS) == 2
    tokens._jwks["retry_after"] = 0.0
    _rechazo(oidc.validar_access_token(idp.token(inventada)))
    assert idp.llamadas(JWKS) == 3


def test_permisos_por_url(idp) -> None:
    token = idp.token()
    assert asyncio.run(oidc.permisos_de(token)) == {"validacion.casos.ejecutar"}
    consulta = idp.peticiones[-1]
    assert consulta.headers["authorization"] == f"Bearer {token}"
    idp.estado_permisos = 401
    error = _rechazo(oidc.permisos_de(token))
    assert (error.status_code, error.detail) == (401, "Token inválido o revocado")
    idp.estado_permisos = 500
    assert _rechazo(oidc.permisos_de(token)).status_code == 502


def test_permisos_por_claim(idp, monkeypatch) -> None:
    monkeypatch.setattr(settings, "oidc_permisos_url", "")
    token = idp.token(permissions=["validacion.tablero.ver", "validacion.aprobar"])
    assert asyncio.run(oidc.permisos_de(token)) == {
        "validacion.tablero.ver",
        "validacion.aprobar",
    }
    monkeypatch.setattr(settings, "oidc_permisos_claim", "roles")
    assert asyncio.run(oidc.permisos_de(idp.token(roles=["a"]))) == {"a"}
    assert asyncio.run(oidc.permisos_de(idp.token())) == set()


def test_permisos_validan_el_token_antes(idp) -> None:
    assert _rechazo(oidc.permisos_de(idp.token(aud="otra"))).status_code == 401
    assert not any("permissions" in str(p.url) for p in idp.peticiones)
