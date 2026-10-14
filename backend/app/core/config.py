from typing import Literal, Self
from urllib.parse import urlsplit

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

OBLIGATORIAS = ("oidc_issuer_url", "oidc_client_id", "oidc_redirect_uri", "oidc_audience")
URLS = ("oidc_issuer_url", "oidc_public_url", "oidc_redirect_uri", "oidc_permisos_url")


def _url_absoluta(valor: str) -> bool:
    partes = urlsplit(valor)
    return partes.scheme in {"http", "https"} and bool(partes.netloc)


class Settings(BaseSettings):
    app_env: Literal["dev", "prod"]
    auth_modo: Literal["oidc", "local"] = "oidc"

    database_path: str = "/data/validacion.sqlite3"
    evidencias_dir: str = "/evidencias"
    contenido_dir: str = "/contenido"

    secret_key: str
    session_cookie_secure: bool = True
    allowed_origins: str = ""
    frontend_url: str
    sesion_minutos: int = 720

    oidc_issuer_url: str = ""
    oidc_public_url: str = ""
    oidc_expected_issuer: str = ""
    oidc_client_id: str = ""
    oidc_client_secret: str = ""
    oidc_redirect_uri: str = ""
    oidc_audience: str = ""
    oidc_scope: str = "openid profile email"
    oidc_token_typ: str = ""
    oidc_permisos_url: str = ""
    oidc_permisos_claim: str = "permissions"

    validacion_lectura_token: str = ""
    cuentas_path: str = "/run/secrets/validacion_cuentas"

    model_config = SettingsConfigDict(secrets_dir="/run/secrets", extra="ignore")

    @field_validator(
        "frontend_url", "oidc_issuer_url", "oidc_public_url", "oidc_expected_issuer"
    )
    @classmethod
    def sin_diagonal_final(cls, valor: str) -> str:
        return valor.rstrip("/")

    @field_validator(
        "secret_key",
        "oidc_client_secret",
        "oidc_client_id",
        "oidc_audience",
        "oidc_token_typ",
        "validacion_lectura_token",
    )
    @classmethod
    def sin_espacios(cls, valor: str) -> str:
        return valor.strip()

    @model_validator(mode="after")
    def modo_coherente(self) -> Self:
        if self.auth_modo == "local" and self.app_env != "dev":
            raise ValueError("AUTH_MODO=local solo se permite con APP_ENV=dev")
        if self.auth_modo == "oidc":
            problemas = [
                f"falta {nombre.upper()}" for nombre in OBLIGATORIAS if not getattr(self, nombre)
            ]
            problemas += [
                f"{nombre.upper()} debe ser una URL absoluta http(s)"
                for nombre in URLS
                if getattr(self, nombre) and not _url_absoluta(getattr(self, nombre))
            ]
            if problemas:
                raise ValueError("AUTH_MODO=oidc incompleto: " + "; ".join(problemas))
        return self

    @property
    def auth_local(self) -> bool:
        return self.auth_modo == "local"

    @property
    def origenes_permitidos(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def oidc_publico(self) -> str:
        return self.oidc_public_url or self.oidc_issuer_url


settings = Settings()
