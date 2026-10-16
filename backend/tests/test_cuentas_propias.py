from datetime import timedelta

import pytest

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.time import utcnow
from app.models import Cuenta, Invitacion, Restablecimiento, Sesion, Usuario
from tests.apoyo_cuentas import CONTRASENA, aceptar, con_csrf, entrar, primer_admin, token_de

NUEVA = "otra-clave-larga-2"


@pytest.fixture
def modo_cuentas(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "auth_modo", "cuentas")


@pytest.fixture
def admin(modo_cuentas, cliente_de):
    return primer_admin(cliente_de(None))


def _invitar(admin, email: str, roles: list[str] | None = None) -> str:
    respuesta = admin.post("/api/admin/invitaciones", json={"email": email, "roles": roles or []})
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()["enlace"]


def _persona_id(email: str) -> int:
    with SessionLocal() as db:
        return db.query(Usuario).filter_by(email=email).one().id


def test_modo_y_rutas_segun_auth_modo(cliente_de, modo_cuentas) -> None:
    anonimo = cliente_de(None)
    assert anonimo.get("/api/auth/modo").json() == {"modo": "cuentas"}
    assert anonimo.get("/api/auth/login", follow_redirects=False).status_code == 404
    assert anonimo.post("/api/auth/local", json={"clave": "validador"}).status_code == 404


def test_en_modo_oidc_no_hay_rutas_de_cuentas(cliente_de, idp) -> None:
    anonimo = cliente_de(None)
    assert entrar(anonimo, "a@b.test") == 404
    assert anonimo.get("/api/auth/invitacion/x").status_code == 404
    assert anonimo.post("/api/auth/restablecer/x", json={"contrasena": NUEVA}).status_code == 404


def test_invitacion_crea_persona_con_roles_y_sesion(admin, cliente_de) -> None:
    enlace = _invitar(admin, "vale@ejemplo.test", ["validador"])
    nueva = cliente_de(None)
    assert nueva.get(f"/api/auth/invitacion/{token_de(enlace)}").json() == {
        "email": "vale@ejemplo.test"
    }
    aceptar(nueva, enlace, "Vale")
    usuario = nueva.get("/api/auth/me").json()["usuario"]
    assert (usuario["nombre"], usuario["origen"], usuario["tiene_cuenta"]) == (
        "Vale",
        "cuenta",
        True,
    )
    assert usuario["permisos"] == ["validacion.casos.ejecutar"]
    otra = cliente_de(None)
    reuso = otra.post(
        f"/api/auth/invitacion/{token_de(enlace)}", json={"nombre": "X", "contrasena": NUEVA}
    )
    assert reuso.status_code == 404
    repetida = admin.post("/api/admin/invitaciones", json={"email": "vale@ejemplo.test"})
    assert repetida.status_code == 409


def test_los_tokens_se_guardan_solo_como_hash(admin) -> None:
    enlace = _invitar(admin, "hash@ejemplo.test")
    with SessionLocal() as db:
        guardado = db.query(Invitacion).filter_by(email="hash@ejemplo.test").one().token_hash
    assert token_de(enlace) not in guardado
    assert len(guardado) == 64


def test_invitacion_expirada_no_sirve(admin, cliente_de) -> None:
    enlace = _invitar(admin, "tarde@ejemplo.test")
    with SessionLocal() as db:
        db.query(Invitacion).filter_by(email="tarde@ejemplo.test").one().expira = utcnow()
        db.commit()
    nueva = cliente_de(None)
    assert nueva.get(f"/api/auth/invitacion/{token_de(enlace)}").status_code == 404


@pytest.mark.parametrize("contrasena", ["corta", "1234567890", "Contraseña", "qwertyuiop"])
def test_contrasenas_debiles_se_rechazan(admin, cliente_de, contrasena: str) -> None:
    enlace = _invitar(admin, "debil@ejemplo.test")
    respuesta = cliente_de(None).post(
        f"/api/auth/invitacion/{token_de(enlace)}", json={"nombre": "D", "contrasena": contrasena}
    )
    assert respuesta.status_code == 422


def test_entrar_y_error_generico(admin, cliente_de) -> None:
    aceptar(cliente_de(None), _invitar(admin, "ana@ejemplo.test"), "Ana")
    cliente = cliente_de(None)
    assert entrar(cliente, "ANA@ejemplo.test") == 200
    assert cliente.get("/api/auth/me").json()["usuario"]["email"] == "ana@ejemplo.test"
    mala = cliente_de(None).post(
        "/api/auth/entrar", json={"email": "ana@ejemplo.test", "contrasena": "equivocada-123"}
    )
    nadie = cliente_de(None).post(
        "/api/auth/entrar", json={"email": "nadie@ejemplo.test", "contrasena": CONTRASENA}
    )
    assert mala.status_code == nadie.status_code == 401
    assert mala.json() == nadie.json() == {"detail": "Correo o contraseña incorrectos"}


def test_limite_de_intentos_por_correo(admin, cliente_de) -> None:
    aceptar(cliente_de(None), _invitar(admin, "lim@ejemplo.test"), "Lim")
    cliente = cliente_de(None)
    for _ in range(5):
        assert entrar(cliente, "lim@ejemplo.test", "equivocada-123") == 401
    assert entrar(cliente, "lim@ejemplo.test") == 429
    with SessionLocal() as db:
        from app.models import IntentoEntrada

        for intento in db.query(IntentoEntrada):
            intento.momento = utcnow() - timedelta(minutes=16)
        db.commit()
    assert entrar(cliente, "lim@ejemplo.test") == 200


def test_limite_de_intentos_por_ip(admin, cliente_de) -> None:
    cliente = cliente_de(None)
    cliente.headers["X-Real-IP"] = "203.0.113.7"
    for numero in range(5):
        assert entrar(cliente, f"p{numero}@ejemplo.test") == 401
    assert entrar(cliente, "otro@ejemplo.test") == 429
    cliente.headers["X-Real-IP"] = "203.0.113.8"
    assert entrar(cliente, "otro@ejemplo.test") == 401


def test_restablecer_por_enlace_de_un_solo_uso(admin, cliente_de) -> None:
    persona = cliente_de(None)
    aceptar(persona, _invitar(admin, "olvido@ejemplo.test"), "Olvido")
    ruta = f"/api/admin/personas/{_persona_id('olvido@ejemplo.test')}/restablecer"
    primero = admin.post(ruta).json()["enlace"]
    enlace = admin.post(ruta).json()
    assert "/restablecer/" in enlace["enlace"]
    anonimo = cliente_de(None)
    viejo = anonimo.post(f"/api/auth/restablecer/{token_de(primero)}", json={"contrasena": NUEVA})
    assert viejo.status_code == 404
    token = token_de(enlace["enlace"])
    assert anonimo.get(f"/api/auth/restablecer/{token}").json() == {"email": "olvido@ejemplo.test"}
    assert (
        anonimo.post(f"/api/auth/restablecer/{token}", json={"contrasena": NUEVA}).status_code
        == 200
    )
    assert anonimo.get("/api/auth/me").status_code == 200
    assert persona.get("/api/auth/me").status_code == 401
    assert entrar(cliente_de(None), "olvido@ejemplo.test") == 401
    assert entrar(cliente_de(None), "olvido@ejemplo.test", NUEVA) == 200
    reuso = anonimo.post(f"/api/auth/restablecer/{token}", json={"contrasena": "tercera-clave-3"})
    assert reuso.status_code == 404


def test_restablecimiento_expirado_no_sirve(admin, cliente_de) -> None:
    aceptar(cliente_de(None), _invitar(admin, "exp@ejemplo.test"), "Exp")
    usuario_id = _persona_id("exp@ejemplo.test")
    enlace = admin.post(f"/api/admin/personas/{usuario_id}/restablecer").json()["enlace"]
    with SessionLocal() as db:
        db.query(Restablecimiento).filter_by(usuario_id=usuario_id).one().expira = utcnow()
        db.commit()
    respuesta = cliente_de(None).post(
        f"/api/auth/restablecer/{token_de(enlace)}", json={"contrasena": NUEVA}
    )
    assert respuesta.status_code == 404


def test_cambiar_la_propia_contrasena(admin, cliente_de) -> None:
    aceptar(cliente_de(None), _invitar(admin, "cambia@ejemplo.test"), "Cambia")
    otra_sesion = cliente_de(None)
    entrar(otra_sesion, "cambia@ejemplo.test")
    cliente = cliente_de(None)
    entrar(cliente, "cambia@ejemplo.test")
    con_csrf(cliente)
    mala = cliente.post("/api/auth/contrasena", json={"actual": "no-es-esta-1", "nueva": NUEVA})
    assert mala.status_code == 400
    debil = cliente.post("/api/auth/contrasena", json={"actual": CONTRASENA, "nueva": "corta"})
    assert debil.status_code == 422
    bien = cliente.post("/api/auth/contrasena", json={"actual": CONTRASENA, "nueva": NUEVA})
    assert bien.status_code == 204
    assert cliente.get("/api/auth/me").status_code == 200
    assert otra_sesion.get("/api/auth/me").status_code == 401
    assert entrar(cliente_de(None), "cambia@ejemplo.test", NUEVA) == 200
    with SessionLocal() as db:
        cuenta = db.get(Cuenta, _persona_id("cambia@ejemplo.test"))
        assert cuenta.hash.startswith("$argon2")


def test_cambiar_contrasena_exige_csrf(admin) -> None:
    del admin.headers["X-CSRF-Token"]
    respuesta = admin.post("/api/auth/contrasena", json={"actual": CONTRASENA, "nueva": NUEVA})
    assert respuesta.status_code == 403


def test_desactivar_cierra_la_sesion_y_bloquea_la_entrada(admin, cliente_de) -> None:
    persona = cliente_de(None)
    aceptar(persona, _invitar(admin, "baja@ejemplo.test"), "Baja")
    ruta = f"/api/admin/personas/{_persona_id('baja@ejemplo.test')}/cuenta"
    assert admin.patch(ruta, json={"activa": False}).json()["cuenta"]["activa"] is False
    assert persona.get("/api/auth/me").status_code == 401
    respuesta = cliente_de(None).post(
        "/api/auth/entrar", json={"email": "baja@ejemplo.test", "contrasena": CONTRASENA}
    )
    assert respuesta.json()["detail"] == "Correo o contraseña incorrectos"
    admin.patch(ruta, json={"activa": True})
    assert entrar(cliente_de(None), "baja@ejemplo.test") == 200
    propia = f"/api/admin/personas/{_persona_id('admin@ejemplo.test')}/cuenta"
    assert admin.patch(propia, json={"activa": False}).status_code == 409


def test_la_sesion_de_cuenta_no_sobrevive_si_se_apagan_las_cuentas(admin, monkeypatch) -> None:
    monkeypatch.setattr(settings, "auth_modo", "local")
    assert admin.get("/api/auth/me").status_code == 401
    with SessionLocal() as db:
        assert db.query(Sesion).filter_by(origen="cuenta").count() == 0


def test_en_modo_ambos_una_persona_tiene_oidc_y_cuenta(cliente_de, idp, monkeypatch) -> None:
    monkeypatch.setattr(settings, "auth_modo", "ambos")
    admin = primer_admin(cliente_de(None))
    from tests.test_roles import _entrar_oidc

    oidc = _entrar_oidc(cliente_de, idp)
    assert oidc.get("/api/auth/me").json()["usuario"]["tiene_cuenta"] is False
    aceptar(cliente_de(None), _invitar(admin, "persona@ejemplo.test", ["aprobacion"]), "Persona")
    with SessionLocal() as db:
        assert db.query(Usuario).filter_by(email="persona@ejemplo.test").count() == 1
    usuario = oidc.get("/api/auth/me").json()["usuario"]
    assert usuario["tiene_cuenta"] is True
    assert usuario["permisos"] == ["validacion.casos.ejecutar", "validacion.herramientas.aprobar"]
    cuenta = cliente_de(None)
    assert entrar(cuenta, "persona@ejemplo.test") == 200
    assert cuenta.get("/api/auth/me").json()["usuario"]["permisos"] == [
        "validacion.herramientas.aprobar"
    ]


def test_invitacion_valida_correo_roles_y_se_puede_revocar(admin, cliente_de) -> None:
    assert admin.post("/api/admin/invitaciones", json={"email": "no-es-correo"}).status_code == 422
    malos = admin.post("/api/admin/invitaciones", json={"email": "a@b.test", "roles": ["x"]})
    assert malos.status_code == 422
    enlace = _invitar(admin, " A@B.test ", ["validador"])
    pendientes = admin.get("/api/admin/invitaciones").json()
    assert [(i["email"], i["roles"]) for i in pendientes] == [("a@b.test", ["validador"])]
    assert admin.delete(f"/api/admin/invitaciones/{pendientes[0]['id']}").status_code == 204
    assert admin.get("/api/admin/invitaciones").json() == []
    assert cliente_de(None).get(f"/api/auth/invitacion/{token_de(enlace)}").status_code == 404
