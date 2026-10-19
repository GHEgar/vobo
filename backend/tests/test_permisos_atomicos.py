import pytest


@pytest.fixture
def admin(cliente_de):
    return cliente_de("administracion")


def _con_rol(cliente_de, admin, permisos: list[str], clave: str = "probado"):
    persona = cliente_de("sin-rol")
    creado = admin.post(
        "/api/admin/roles", json={"clave": clave, "nombre": clave, "permisos": permisos}
    )
    assert creado.status_code == 201
    usuario = next(
        p for p in admin.get("/api/admin/personas").json() if p["email"] == "sinrol@local.test"
    )
    assert (
        admin.put(f"/api/admin/personas/{usuario['id']}/roles", json={"roles": [clave]}).status_code
        == 200
    )
    return persona, usuario


def _me(cliente) -> dict:
    return cliente.get("/api/auth/me").json()["usuario"]


def test_pantalla_solo_ve_participacion(cliente_de, admin) -> None:
    persona = cliente_de("sin-rol")
    usuario = next(
        p for p in admin.get("/api/admin/personas").json() if p["email"] == "sinrol@local.test"
    )
    assert (
        admin.put(
            f"/api/admin/personas/{usuario['id']}/roles", json={"roles": ["pantalla"]}
        ).status_code
        == 200
    )
    assert _me(persona)["paginas"] == ["participacion"]
    assert persona.get("/api/participacion").status_code == 200
    assert persona.get("/api/fallas").status_code == 403
    assert persona.get("/api/tablero").status_code == 403
    assert persona.get("/api/admin/personas").status_code == 403


def test_identidad_edita_marca_y_colores_pero_no_ajustes(cliente_de, admin) -> None:
    persona = cliente_de("sin-rol")
    usuario = next(
        p for p in admin.get("/api/admin/personas").json() if p["email"] == "sinrol@local.test"
    )
    admin.put(f"/api/admin/personas/{usuario['id']}/roles", json={"roles": ["identidad"]})
    assert "admin" in _me(persona)["paginas"]
    assert persona.get("/api/admin/configuracion").status_code == 200
    ok = persona.put(
        "/api/admin/configuracion", json={"producto": "Otro nombre", "color_tema": "#112233"}
    )
    assert ok.status_code == 200
    assert persona.put("/api/admin/configuracion", json={"cuentas": []}).status_code == 403
    assert persona.delete("/api/admin/configuracion/cuentas").status_code == 403
    assert persona.delete("/api/admin/configuracion/producto").status_code == 200
    assert persona.get("/api/admin/personas").status_code == 403
    assert persona.get("/api/admin/proyectos").status_code == 403


def test_configuracion_edita_ajustes_pero_no_identidad(cliente_de, admin) -> None:
    persona, _ = _con_rol(cliente_de, admin, ["validacion.configuracion.editar"])
    assert persona.put("/api/admin/configuracion", json={"cuentas": []}).status_code == 200
    assert persona.put("/api/admin/configuracion", json={"producto": "X"}).status_code == 403


def test_proyectos_sin_el_resto_de_administracion(cliente_de, admin) -> None:
    persona, _ = _con_rol(cliente_de, admin, ["validacion.proyectos.gestionar"])
    assert persona.get("/api/admin/proyectos").status_code == 200
    assert (
        persona.post("/api/admin/proyectos", json={"clave": "nuevo", "nombre": "Nuevo"}).status_code
        != 403
    )
    assert persona.get("/api/admin/roles").status_code == 403
    assert persona.get("/api/admin/configuracion").status_code == 403


def test_ver_fallas_sin_gestionarlas(cliente_de, admin, ronda_id) -> None:
    validador = cliente_de("validador")
    falla = validador.post(
        "/api/fallas",
        data={
            "ronda_id": ronda_id,
            "caso_id": "C-CAT-01",
            "obtenido": "No filtra",
            "tipo": "falla",
            "reproducible": "siempre",
        },
    )
    assert falla.status_code == 201, falla.text
    falla = falla.json()
    persona, _ = _con_rol(cliente_de, admin, ["validacion.fallas.ver"])
    assert persona.get(f"/api/fallas?ronda={ronda_id}").status_code == 200
    assert (
        persona.patch(f"/api/fallas/{falla['id']}", json={"estado": "cerrada"}).status_code == 403
    )
    assert persona.post("/api/rondas", json={"nombre": "R2", "snapshot": "s"}).status_code == 403


def test_nadie_otorga_lo_que_no_tiene(cliente_de, admin) -> None:
    persona, usuario = _con_rol(
        cliente_de,
        admin,
        ["validacion.personas.gestionar", "validacion.roles.gestionar"],
        clave="gestor",
    )
    assert persona.get("/api/admin/personas").status_code == 200
    propio = persona.put(
        f"/api/admin/personas/{usuario['id']}/roles", json={"roles": ["gestor", "administracion"]}
    )
    assert propio.status_code == 403
    assert "No puedes otorgar" in propio.json()["detail"]
    escalar = persona.post(
        "/api/admin/roles",
        json={"clave": "todo", "nombre": "Todo", "permisos": ["validacion.admin"]},
    )
    assert escalar.status_code == 403
    menor = persona.post(
        "/api/admin/roles",
        json={"clave": "menor", "nombre": "Menor", "permisos": ["validacion.roles.gestionar"]},
    )
    assert menor.status_code == 201
    roles = {r["clave"]: r["id"] for r in persona.get("/api/admin/roles").json()}
    assert (
        persona.patch(
            f"/api/admin/roles/{roles['menor']}", json={"permisos": ["validacion.identidad.editar"]}
        ).status_code
        == 403
    )
    assert persona.delete(f"/api/admin/roles/{roles['coordinacion']}").status_code in (403, 409)


def test_coordinacion_conserva_rondas_accesos_y_participacion(cliente_de) -> None:
    coordinacion = cliente_de("coordinacion")
    permisos = set(_me(coordinacion)["permisos"])
    assert {
        "validacion.fallas.ver",
        "validacion.rondas.gestionar",
        "validacion.accesos.gestionar",
        "validacion.participacion.ver",
    } <= permisos
    assert (
        coordinacion.post("/api/rondas", json={"nombre": "R", "snapshot": "s"}).status_code == 201
    )
    assert coordinacion.get("/api/accesos").status_code == 200
    assert coordinacion.get("/api/participacion").status_code == 200
