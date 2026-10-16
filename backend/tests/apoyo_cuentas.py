import re

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.crear_admin import invitacion_inicial

CONTRASENA = "una-clave-larga-1"


def token_de(enlace: str) -> str:
    return re.sub(r"^.*/", "", enlace)


def con_csrf(cliente: TestClient) -> TestClient:
    cliente.headers["X-CSRF-Token"] = cliente.get("/api/auth/me").json()["csrf_token"]
    return cliente


def aceptar(cliente: TestClient, enlace: str, nombre: str, contrasena: str = CONTRASENA) -> None:
    respuesta = cliente.post(
        f"/api/auth/invitacion/{token_de(enlace)}",
        json={"nombre": nombre, "contrasena": contrasena},
    )
    assert respuesta.status_code == 200, respuesta.text
    con_csrf(cliente)


def primer_admin(cliente: TestClient, email: str = "admin@ejemplo.test") -> TestClient:
    with SessionLocal() as db:
        enlace = invitacion_inicial(db, email)
    aceptar(cliente, enlace, "Admin Inicial")
    return cliente


def entrar(cliente: TestClient, email: str, contrasena: str = CONTRASENA) -> int:
    return cliente.post(
        "/api/auth/entrar", json={"email": email, "contrasena": contrasena}
    ).status_code
