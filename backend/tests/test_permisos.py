import pytest
from pydantic import ValidationError

from app.core.config import Settings
from tests.conftest import TOKEN_LECTURA


def test_anonimo_recibe_401(cliente_de) -> None:
    assert cliente_de(None).get("/api/contenido").status_code == 401


def test_validador_no_ve_tablero_ni_fallas(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    assert validador.get(f"/api/tablero?ronda={ronda_id}").status_code == 403
    assert validador.get("/api/fallas").status_code == 403
    assert validador.patch("/api/fallas/1", json={"estado": "cerrada"}).status_code == 403


def test_sin_rol_no_marca_casos(cliente_de, ronda_id) -> None:
    sin_rol = cliente_de("sin-rol")
    respuesta = sin_rol.put(
        "/api/resultados/A-GEN-01", json={"ronda_id": ronda_id, "estado": "pasa"}
    )
    assert respuesta.status_code == 403


def test_token_de_lectura_solo_lee(cliente_de, ronda_id) -> None:
    anonimo = cliente_de(None)
    cabecera = {"Authorization": f"Bearer {TOKEN_LECTURA}"}
    assert anonimo.get("/api/fallas", headers=cabecera).status_code == 200
    assert anonimo.get(f"/api/tablero?ronda={ronda_id}", headers=cabecera).status_code == 200
    assert anonimo.get("/api/fallas", headers={"Authorization": "Bearer otro"}).status_code == 401
    assert (
        anonimo.patch("/api/fallas/1", json={"estado": "cerrada"}, headers=cabecera).status_code
        == 401
    )


def test_modo_local_se_rechaza_fuera_de_dev() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="prod", auth_modo="local", secret_key="x", frontend_url="http://x")


def test_modo_oidc_explica_lo_que_falta() -> None:
    with pytest.raises(ValidationError) as error:
        Settings(
            app_env="prod",
            auth_modo="oidc",
            secret_key="x",
            frontend_url="http://x",
            oidc_issuer_url="idp-sin-esquema",
            oidc_client_id="c",
            oidc_redirect_uri="https://vobo.ejemplo/api/auth/callback",
        )
    mensaje = str(error.value)
    assert "OIDC_AUDIENCE" in mensaje
    assert "OIDC_ISSUER_URL debe ser una URL absoluta" in mensaje
