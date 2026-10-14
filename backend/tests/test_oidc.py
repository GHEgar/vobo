import asyncio
import base64
import hashlib
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest

from app.core import oidc
from app.core.config import settings
from app.core.oidc import descubrimiento, http
from tests.idp_falso import INTERNA, PUBLICA


def _correr(corrutina):
    return asyncio.run(corrutina)


def test_discovery_reescribe_lo_del_servidor_a_la_url_interna(idp) -> None:
    endpoints = _correr(descubrimiento.endpoints())
    assert endpoints.autorizacion == f"{PUBLICA}/auth/authorize"
    assert endpoints.token == f"{INTERNA}/auth/token"
    assert endpoints.jwks == f"{INTERNA}/.well-known/jwks.json"
    assert endpoints.revocacion == f"{INTERNA}/auth/revoke"
    _correr(descubrimiento.endpoints())
    assert idp.llamadas(f"{INTERNA}/.well-known/openid-configuration") == 1
    assert all(urlsplit(str(p.url)).netloc != "idp.ejemplo" for p in idp.peticiones)


def test_sin_url_publica_no_se_reescribe(idp, monkeypatch) -> None:
    monkeypatch.setattr(settings, "oidc_public_url", "")
    idp.descubrimiento = {
        **idp.descubrimiento,
        "token_endpoint": f"{INTERNA}/auth/token",
        "authorization_endpoint": f"{INTERNA}/auth/authorize",
    }
    endpoints = _correr(descubrimiento.endpoints())
    assert endpoints.token == f"{INTERNA}/auth/token"
    assert endpoints.autorizacion == f"{INTERNA}/auth/authorize"


def test_autorizacion_interna_sale_publica_al_navegador(idp) -> None:
    idp.descubrimiento = {
        **idp.descubrimiento,
        "authorization_endpoint": f"{INTERNA}/auth/authorize",
    }
    assert _correr(descubrimiento.endpoints()).autorizacion == f"{PUBLICA}/auth/authorize"


def test_discovery_incompleto_es_error_oidc(idp) -> None:
    idp.descubrimiento = {"issuer": PUBLICA}
    with pytest.raises(oidc.ErrorOIDC) as error:
        _correr(descubrimiento.endpoints())
    assert "token_endpoint" in error.value.description


def test_url_de_autorizacion_con_pkce_y_state(idp) -> None:
    solicitud = _correr(oidc.solicitud_de_autorizacion())
    partes = urlsplit(solicitud.url)
    assert f"{partes.scheme}://{partes.netloc}{partes.path}" == f"{PUBLICA}/auth/authorize"
    query = {k: v[0] for k, v in parse_qs(partes.query).items()}
    resumen = hashlib.sha256(solicitud.code_verifier.encode()).digest()
    desafio = base64.urlsafe_b64encode(resumen).rstrip(b"=").decode()
    assert query == {
        "client_id": "cliente-validacion",
        "redirect_uri": "http://testserver/api/auth/callback",
        "response_type": "code",
        "scope": "openid profile email",
        "state": solicitud.state,
        "code_challenge": desafio,
        "code_challenge_method": "S256",
    }


def test_canje_usa_client_secret_post(idp) -> None:
    tokens = _correr(oidc.canjear_codigo("codigo-1", "verificador-1"))
    assert tokens["refresh_token"] == "refresco-1"
    assert idp.formularios[-1] == {
        "grant_type": "authorization_code",
        "code": "codigo-1",
        "redirect_uri": "http://testserver/api/auth/callback",
        "code_verifier": "verificador-1",
        "client_id": "cliente-validacion",
        "client_secret": "secreto-validacion",
    }


def test_refresco_y_errores_del_proveedor(idp) -> None:
    _correr(oidc.refrescar("refresco-1"))
    assert idp.formularios[-1]["grant_type"] == "refresh_token"
    assert idp.formularios[-1]["refresh_token"] == "refresco-1"
    idp.respuesta_token = (400, {"error": "invalid_grant", "error_description": "vencido"})
    with pytest.raises(oidc.ErrorOIDC) as error:
        _correr(oidc.refrescar("refresco-1"))
    assert (error.value.error, error.value.description, error.value.status_code) == (
        "invalid_grant",
        "vencido",
        400,
    )
    idp.respuesta_token = (503, {})
    with pytest.raises(oidc.ErrorOIDC) as error:
        _correr(oidc.refrescar("refresco-1"))
    assert error.value.status_code == 503


def test_sin_conexion_no_trae_status(idp, monkeypatch) -> None:
    _correr(descubrimiento.endpoints())

    def caido(_peticion: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("caido")

    monkeypatch.setattr(http, "transporte", httpx.MockTransport(caido))
    with pytest.raises(oidc.ErrorOIDC) as error:
        _correr(oidc.refrescar("refresco-1"))
    assert error.value.error == "connection_error"
    assert error.value.status_code is None


def test_revocar_envia_el_token_e_ignora_errores(idp, monkeypatch) -> None:
    _correr(oidc.revocar("refresco-1"))
    assert idp.formularios[-1] == {
        "client_id": "cliente-validacion",
        "client_secret": "secreto-validacion",
        "token": "refresco-1",
    }

    def roto(_peticion: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="no")

    monkeypatch.setattr(http, "transporte", httpx.MockTransport(roto))
    _correr(oidc.revocar("refresco-1"))


def test_sin_endpoint_de_revocacion_no_llama(idp) -> None:
    idp.descubrimiento = {
        k: v for k, v in idp.descubrimiento.items() if k != "revocation_endpoint"
    }
    _correr(oidc.revocar("refresco-1"))
    assert idp.llamadas(f"{INTERNA}/auth/revoke") == 0
