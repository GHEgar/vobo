import os
import tempfile
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from tests.idp_falso import IdpFalso

_TMP = Path(tempfile.mkdtemp(prefix="vobo-tests-"))
RAIZ_REPO = Path(__file__).resolve().parents[2]
CONTENIDO = RAIZ_REPO / "ejemplo" / "contenido"
TOKEN_LECTURA = "token-de-prueba-solo-lectura"

os.environ.update(
    {
        "APP_ENV": "dev",
        "AUTH_MODO": "local",
        "DATABASE_PATH": str(_TMP / "validacion.sqlite3"),
        "EVIDENCIAS_DIR": str(_TMP / "evidencias"),
        "CONTENIDO_DIR": str(CONTENIDO),
        "SECRET_KEY": "clave-de-pruebas",
        "SESSION_COOKIE_SECURE": "false",
        "FRONTEND_URL": "http://testserver",
        "VALIDACION_LECTURA_TOKEN": TOKEN_LECTURA,
    }
)


@pytest.fixture(autouse=True)
def base_limpia() -> Iterator[None]:
    from alembic import command

    from app.core import migraciones
    from app.core.database import Base, SessionLocal, engine
    from app.services import proyectos, roles

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conexion:
        command.stamp(migraciones.configuracion(conexion), "head")
    with SessionLocal() as db:
        roles.sembrar_sistema(db)
        proyectos.asegurar_por_omision(db)
    yield


@pytest.fixture
def cliente_de() -> Iterator[Callable[[str | None], TestClient]]:
    from app.main import app

    abiertos: list[TestClient] = []

    def crear(clave: str | None) -> TestClient:
        cliente = TestClient(app)
        cliente.__enter__()
        abiertos.append(cliente)
        if clave is None:
            return cliente
        assert cliente.post("/api/auth/local", json={"clave": clave}).status_code == 200
        sesion = cliente.get("/api/auth/me").json()
        cliente.headers["X-CSRF-Token"] = sesion["csrf_token"]
        return cliente

    yield crear
    for cliente in abiertos:
        cliente.__exit__(None, None, None)


@pytest.fixture
def ronda_id(cliente_de: Callable[[str | None], TestClient]) -> int:
    coordinacion = cliente_de("coordinacion")
    respuesta = coordinacion.post("/api/rondas", json={"nombre": "Ronda 1", "snapshot": "s1"})
    assert respuesta.status_code == 201
    return respuesta.json()["id"]


@pytest.fixture
def idp(monkeypatch: pytest.MonkeyPatch) -> Iterator[IdpFalso]:
    import httpx

    from app.core import oidc
    from app.core.config import settings
    from app.core.oidc import http
    from tests.idp_falso import INTERNA, PERMISOS_URL, PUBLICA

    falso = IdpFalso()
    configuracion = {
        "auth_modo": "oidc",
        "oidc_issuer_url": INTERNA,
        "oidc_public_url": PUBLICA,
        "oidc_expected_issuer": PUBLICA,
        "oidc_client_id": "cliente-validacion",
        "oidc_client_secret": "secreto-validacion",
        "oidc_redirect_uri": "http://testserver/api/auth/callback",
        "oidc_audience": "validacion",
        "oidc_token_typ": "access",
        "oidc_permisos_url": PERMISOS_URL,
    }
    for nombre, valor in configuracion.items():
        monkeypatch.setattr(settings, nombre, valor)
    monkeypatch.setattr(http, "transporte", httpx.MockTransport(falso))
    oidc.olvidar_caches()
    yield falso
    oidc.olvidar_caches()


@pytest.fixture
def en_base(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[Path]:
    from app.core.config import settings
    from app.services import contenido_base

    media = tmp_path / "media-base"
    monkeypatch.setattr(settings, "contenido_fuente", "base")
    monkeypatch.setattr(settings, "media_dir", str(media))
    contenido_base.cache.olvidar()
    yield media
    contenido_base.cache.olvidar()
