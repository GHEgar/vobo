from urllib.parse import parse_qs, urlsplit

import pytest
from pydantic import ValidationError

from app.core.config import Settings, settings
from app.core.database import SessionLocal
from app.core.permisos import TODOS_CON_ADMIN, expandir
from app.models import Rol, Usuario, UsuarioRol

COORDINACION = [
    "validacion.casos.ejecutar",
    "validacion.fallas.gestionar",
    "validacion.tablero.ver",
]


def _entrar_oidc(cliente_de, idp):
    cliente = cliente_de(None)
    login = cliente.get("/api/auth/login", follow_redirects=False)
    estado = parse_qs(urlsplit(login.headers["location"]).query)["state"][0]
    cliente.get(f"/api/auth/callback?code=c&state={estado}", follow_redirects=False)
    return cliente


def _asignar(email: str, clave: str) -> None:
    with SessionLocal() as db:
        usuario = db.query(Usuario).filter_by(email=email).one()
        rol = db.query(Rol).filter_by(clave=clave).one()
        db.add(UsuarioRol(usuario_id=usuario.id, rol_id=rol.id))
        db.commit()


@pytest.mark.parametrize(
    ("permisos", "paginas"),
    [
        (["validacion.casos.ejecutar"], []),
        (
            COORDINACION,
            [
                "aprobaciones",
                "fallas",
                "herramientas",
                "participacion",
                "rondas",
                "tablero",
                "tecnico",
            ],
        ),
        (
            ["validacion.herramientas.aprobar"],
            ["aprobaciones", "fallas", "herramientas", "participacion", "tablero"],
        ),
    ],
)
def test_sin_configuracion_nueva_queda_igual_que_hoy(cliente_de, idp, permisos, paginas) -> None:
    idp.permisos = permisos
    idp.claims = {"groups": ["equipo-coordinacion"]}
    usuario = _entrar_oidc(cliente_de, idp).get("/api/auth/me").json()["usuario"]
    assert usuario["permisos"] == sorted(expandir(set(permisos)))
    assert usuario["paginas"] == paginas
    assert usuario["origen"] == "oidc"
    assert usuario["tiene_cuenta"] is False
    with SessionLocal() as db:
        assert db.query(Usuario).one().permisos == sorted(expandir(set(permisos)))


def test_los_roles_asignados_se_suman_a_los_del_proveedor(cliente_de, idp) -> None:
    cliente = _entrar_oidc(cliente_de, idp)
    _asignar("persona@ejemplo.test", "aprobacion")
    permisos = cliente.get("/api/auth/me").json()["usuario"]["permisos"]
    assert permisos == ["validacion.casos.ejecutar", "validacion.herramientas.aprobar"]


def test_los_grupos_mapeados_dan_los_permisos_del_rol(cliente_de, idp, monkeypatch) -> None:
    monkeypatch.setattr(settings, "oidc_roles_claim", "groups")
    monkeypatch.setattr(
        settings,
        "oidc_roles_mapa",
        '{"equipo-coordinacion": "coordinacion", "otro": "rol-que-no-existe"}',
    )
    idp.permisos = []
    idp.claims = {"groups": ["equipo-coordinacion", "otro", "sin-mapa"]}
    usuario = _entrar_oidc(cliente_de, idp).get("/api/auth/me").json()["usuario"]
    assert usuario["permisos"] == sorted(expandir(set(COORDINACION)))
    assert "rondas" in usuario["paginas"]


def test_el_claim_de_grupos_puede_ser_texto(cliente_de, idp, monkeypatch) -> None:
    monkeypatch.setattr(settings, "oidc_roles_claim", "roles_app")
    monkeypatch.setattr(settings, "oidc_roles_mapa", '{"aprueba": "aprobacion"}')
    idp.claims = {"roles_app": "aprueba lee"}
    permisos = _entrar_oidc(cliente_de, idp).get("/api/auth/me").json()["usuario"]["permisos"]
    assert "validacion.herramientas.aprobar" in permisos


def test_administracion_implica_todos_los_permisos(cliente_de) -> None:
    usuario = cliente_de("administracion").get("/api/auth/me").json()["usuario"]
    assert set(usuario["permisos"]) == TODOS_CON_ADMIN
    assert "admin" in usuario["paginas"]
    assert {"tablero", "fallas", "rondas", "aprobaciones"} <= set(usuario["paginas"])


def test_administracion_por_grupo_tambien_implica_todo(cliente_de, idp, monkeypatch) -> None:
    monkeypatch.setattr(settings, "oidc_roles_claim", "groups")
    monkeypatch.setattr(settings, "oidc_roles_mapa", '{"ti": "administracion"}')
    idp.claims = {"groups": ["ti"]}
    usuario = _entrar_oidc(cliente_de, idp).get("/api/auth/me").json()["usuario"]
    assert set(usuario["permisos"]) == TODOS_CON_ADMIN


def test_quien_no_es_admin_no_ve_la_pagina(cliente_de) -> None:
    assert (
        "admin" not in cliente_de("coordinacion").get("/api/auth/me").json()["usuario"]["paginas"]
    )


@pytest.mark.parametrize("mapa", ["no-json", "[1, 2]", '{"grupo": 3}'])
def test_mapa_de_roles_invalido_se_rechaza(mapa: str) -> None:
    with pytest.raises(ValidationError, match="OIDC_ROLES_MAPA"):
        Settings(
            app_env="dev",
            auth_modo="local",
            secret_key="x",
            frontend_url="http://x",
            oidc_roles_mapa=mapa,
        )


def test_modo_cuentas_no_exige_oidc_y_ambos_si() -> None:
    base = {"app_env": "prod", "secret_key": "x", "frontend_url": "http://x"}
    assert Settings(**base, auth_modo="cuentas").auth_cuentas
    with pytest.raises(ValidationError, match="AUTH_MODO=ambos incompleto"):
        Settings(**base, auth_modo="ambos")
