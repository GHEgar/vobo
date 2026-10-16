import pytest

from app import crear_admin
from app.core.config import settings
from app.core.database import SessionLocal
from tests.apoyo_cuentas import aceptar, token_de


def test_fuera_de_cuentas_no_se_puede(capsys) -> None:
    assert crear_admin.main(["admin@ejemplo.test"]) == 1
    assert "AUTH_MODO" in capsys.readouterr().err


def test_imprime_un_enlace_de_administracion(monkeypatch, capsys, cliente_de) -> None:
    monkeypatch.setattr(settings, "auth_modo", "cuentas")
    assert crear_admin.main(["Admin@Ejemplo.test"]) == 0
    enlace = capsys.readouterr().out.strip().splitlines()[-1]
    assert enlace.startswith("http://testserver/invitacion/")
    cliente = cliente_de(None)
    assert cliente.get(f"/api/auth/invitacion/{token_de(enlace)}").json() == {
        "email": "admin@ejemplo.test"
    }
    aceptar(cliente, enlace, "Admin")
    usuario = cliente.get("/api/auth/me").json()["usuario"]
    assert "validacion.admin" in usuario["permisos"]
    assert "admin" in usuario["paginas"]
    assert crear_admin.main(["otra@ejemplo.test"]) == 1
    assert "Ya hay" in capsys.readouterr().err


def test_correo_invalido_se_rechaza(monkeypatch) -> None:
    monkeypatch.setattr(settings, "auth_modo", "cuentas")
    with SessionLocal() as db, pytest.raises(ValueError):
        crear_admin.invitacion_inicial(db, "no-es-correo")


def test_no_hay_forma_web_de_crear_admin_sin_token(monkeypatch, cliente_de) -> None:
    monkeypatch.setattr(settings, "auth_modo", "cuentas")
    anonimo = cliente_de(None)
    assert anonimo.post("/api/admin/invitaciones", json={"email": "a@b.test"}).status_code == 401
    falso = anonimo.post(
        "/api/auth/invitacion/inventado", json={"nombre": "X", "contrasena": "clave-larga-99"}
    )
    assert falso.status_code == 404
    assert anonimo.post("/api/admin/roles", json={"clave": "x1", "nombre": "X"}).status_code == 401
