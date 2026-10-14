from urllib.parse import parse_qs, urlsplit

from app.core.database import SessionLocal
from app.models.usuario import Sesion, Usuario
from tests.idp_falso import INTERNA, PUBLICA


def _entrar(cliente_de, idp):
    cliente = cliente_de(None)
    login = cliente.get("/api/auth/login", follow_redirects=False)
    assert login.status_code == 302
    destino = login.headers["location"]
    assert destino.startswith(f"{PUBLICA}/auth/authorize?")
    estado = parse_qs(urlsplit(destino).query)["state"][0]
    callback = cliente.get(
        f"/api/auth/callback?code=codigo-1&state={estado}", follow_redirects=False
    )
    assert callback.status_code == 302
    assert callback.headers["location"] == "http://testserver/"
    return cliente


def test_flujo_completo_crea_la_sesion(cliente_de, idp) -> None:
    assert cliente_de(None).get("/api/auth/modo").json() == {"modo": "oidc"}
    cliente = _entrar(cliente_de, idp)
    assert idp.formularios[-1]["client_secret"] == "secreto-validacion"
    me = cliente.get("/api/auth/me")
    assert me.status_code == 200
    usuario = me.json()["usuario"]
    assert usuario["email"] == "persona@ejemplo.test"
    assert usuario["permisos"] == ["validacion.casos.ejecutar"]
    with SessionLocal() as db:
        guardado = db.query(Usuario).one()
        assert guardado.sub_oidc == "u-1"
        assert db.query(Sesion).one().refresh_token == "refresco-1"


def test_estado_distinto_da_400(cliente_de, idp) -> None:
    cliente = cliente_de(None)
    cliente.get("/api/auth/login", follow_redirects=False)
    respuesta = cliente.get("/api/auth/callback?code=c&state=otro", follow_redirects=False)
    assert respuesta.status_code == 400


def test_callback_sin_transaccion_reintenta_una_vez(cliente_de, idp) -> None:
    cliente = cliente_de(None)
    primera = cliente.get("/api/auth/callback?code=c&state=s", follow_redirects=False)
    assert primera.status_code == 302
    assert primera.headers["location"] == "/api/auth/login"
    segunda = cliente.get("/api/auth/callback?code=c&state=s", follow_redirects=False)
    assert segunda.status_code == 400


def test_canje_rechazado_da_502_sin_nombrar_al_proveedor(cliente_de, idp) -> None:
    idp.respuesta_token = (400, {"error": "invalid_grant"})
    cliente = cliente_de(None)
    login = cliente.get("/api/auth/login", follow_redirects=False)
    estado = parse_qs(urlsplit(login.headers["location"]).query)["state"][0]
    respuesta = cliente.get(f"/api/auth/callback?code=c&state={estado}", follow_redirects=False)
    assert respuesta.status_code == 502
    assert respuesta.json()["detail"] == "No se pudo completar el inicio de sesión"


def test_permiso_revocado_da_401(cliente_de, idp) -> None:
    cliente = _entrar(cliente_de, idp)
    idp.estado_permisos = 401
    respuesta = cliente.get("/api/auth/me")
    assert (respuesta.status_code, respuesta.json()["detail"]) == (
        401,
        "Token inválido o revocado",
    )


def test_refresco_rechazado_cierra_la_sesion(cliente_de, idp) -> None:
    cliente = _entrar(cliente_de, idp)
    with SessionLocal() as db:
        sesion = db.query(Sesion).one()
        sesion.access_expira = sesion.created_at
        db.commit()
    idp.respuesta_token = (400, {"error": "invalid_grant"})
    assert cliente.get("/api/auth/me").status_code == 401
    with SessionLocal() as db:
        assert db.query(Sesion).count() == 0


def test_refresco_con_proveedor_caido_da_503(cliente_de, idp) -> None:
    cliente = _entrar(cliente_de, idp)
    with SessionLocal() as db:
        sesion = db.query(Sesion).one()
        sesion.access_expira = sesion.created_at
        db.commit()
    idp.respuesta_token = (503, {})
    assert cliente.get("/api/auth/me").status_code == 503
    idp.respuesta_token = None
    assert cliente.get("/api/auth/me").status_code == 200


def test_logout_revoca_el_refresh_token(cliente_de, idp) -> None:
    cliente = _entrar(cliente_de, idp)
    csrf = cliente.get("/api/auth/me").json()["csrf_token"]
    salida = cliente.post("/api/auth/logout", headers={"X-CSRF-Token": csrf})
    assert salida.status_code == 200
    assert idp.llamadas(f"{INTERNA}/auth/revoke") == 1
    assert idp.formularios[-1]["token"] == "refresco-1"
    assert cliente.get("/api/auth/me").status_code == 401
