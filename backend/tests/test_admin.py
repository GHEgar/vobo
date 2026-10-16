import pytest


@pytest.fixture
def admin(cliente_de):
    return cliente_de("administracion")


def _persona(cliente, email: str) -> dict:
    return next(p for p in cliente.get("/api/admin/personas").json() if p["email"] == email)


@pytest.mark.parametrize(
    ("metodo", "ruta"),
    [
        ("get", "/api/admin/roles"),
        ("get", "/api/admin/personas"),
        ("get", "/api/admin/permisos"),
        ("post", "/api/admin/roles"),
        ("delete", "/api/admin/roles/1"),
        ("post", "/api/admin/invitaciones"),
    ],
)
def test_sin_permiso_de_admin_recibe_403(cliente_de, metodo: str, ruta: str) -> None:
    respuesta = getattr(cliente_de("coordinacion"), metodo)(ruta)
    assert respuesta.status_code == 403
    assert getattr(cliente_de(None), metodo)(ruta).status_code == 401


def test_mutaciones_exigen_csrf(admin) -> None:
    del admin.headers["X-CSRF-Token"]
    nuevo = {"clave": "lectura", "nombre": "Lectura", "permisos": []}
    assert admin.post("/api/admin/roles", json=nuevo).status_code == 403
    assert admin.get("/api/admin/roles").status_code == 200


def test_lista_los_roles_de_sistema_y_el_catalogo(admin) -> None:
    roles = admin.get("/api/admin/roles").json()
    assert [r["clave"] for r in roles] == [
        "validador",
        "coordinacion",
        "aprobacion",
        "administracion",
    ]
    assert all(r["sistema"] for r in roles)
    catalogo = admin.get("/api/admin/permisos").json()
    assert {p["clave"] for p in catalogo} == {
        "validacion.casos.ejecutar",
        "validacion.tablero.ver",
        "validacion.fallas.gestionar",
        "validacion.herramientas.aprobar",
        "validacion.contenido.editar",
    }
    assert all(p["descripcion"] for p in catalogo)


def test_crea_edita_y_borra_un_rol_propio(admin) -> None:
    creado = admin.post(
        "/api/admin/roles",
        json={"clave": "lectura", "nombre": "Lectura", "permisos": ["validacion.tablero.ver"]},
    )
    assert creado.status_code == 201
    rol = creado.json()
    assert rol["sistema"] is False
    repetido = admin.post("/api/admin/roles", json={"clave": "lectura", "nombre": "Otra"})
    assert repetido.status_code == 409
    editado = admin.patch(
        f"/api/admin/roles/{rol['id']}",
        json={"nombre": "Solo tablero", "clave": "otra", "permisos": ["validacion.admin"]},
    )
    assert editado.status_code == 422
    editado = admin.patch(
        f"/api/admin/roles/{rol['id']}", json={"nombre": "Solo tablero", "clave": "otra"}
    )
    assert editado.json()["clave"] == "lectura"
    assert editado.json()["nombre"] == "Solo tablero"
    assert admin.delete(f"/api/admin/roles/{rol['id']}").status_code == 204
    assert admin.delete(f"/api/admin/roles/{rol['id']}").status_code == 404


def test_los_roles_de_sistema_no_se_borran_y_administracion_no_cambia(admin) -> None:
    roles = {r["clave"]: r for r in admin.get("/api/admin/roles").json()}
    for rol in roles.values():
        assert admin.delete(f"/api/admin/roles/{rol['id']}").status_code == 409
    administracion = roles["administracion"]["id"]
    respuesta = admin.patch(f"/api/admin/roles/{administracion}", json={"permisos": []})
    assert respuesta.status_code == 409
    validador = admin.patch(
        f"/api/admin/roles/{roles['validador']['id']}",
        json={"permisos": ["validacion.casos.ejecutar", "validacion.tablero.ver"]},
    )
    assert validador.status_code == 200
    assert validador.json()["clave"] == "validador"


def test_asignar_roles_cambia_los_permisos_de_la_persona(admin, cliente_de) -> None:
    validador = cliente_de("validador")
    persona = _persona(admin, "validador@local.test")
    respuesta = admin.put(
        f"/api/admin/personas/{persona['id']}/roles", json={"roles": ["aprobacion"]}
    )
    assert respuesta.json()["roles"] == ["aprobacion"]
    permisos = validador.get("/api/auth/me").json()["usuario"]["permisos"]
    assert "validacion.herramientas.aprobar" in permisos
    desconocido = admin.put(f"/api/admin/personas/{persona['id']}/roles", json={"roles": ["x"]})
    assert desconocido.status_code == 422
    admin.put(f"/api/admin/personas/{persona['id']}/roles", json={"roles": []})
    permisos = validador.get("/api/auth/me").json()["usuario"]["permisos"]
    assert permisos == ["validacion.casos.ejecutar"]


def test_no_se_quita_administracion_a_la_ultima_persona(admin, cliente_de) -> None:
    cliente_de("validador")
    persona = _persona(admin, "validador@local.test")
    ruta = f"/api/admin/personas/{persona['id']}/roles"
    assert admin.put(ruta, json={"roles": ["administracion"]}).status_code == 200
    otra = _persona(admin, "administracion@local.test")
    otra_ruta = f"/api/admin/personas/{otra['id']}/roles"
    assert admin.put(otra_ruta, json={"roles": ["administracion"]}).status_code == 200
    assert admin.put(ruta, json={"roles": []}).status_code == 200
    assert admin.put(otra_ruta, json={"roles": []}).status_code == 409


def test_invitar_y_restablecer_exigen_cuentas_habilitadas(admin) -> None:
    respuesta = admin.post("/api/admin/invitaciones", json={"email": "x@ejemplo.test"})
    assert respuesta.status_code == 409
    persona = _persona(admin, "administracion@local.test")
    assert admin.post(f"/api/admin/personas/{persona['id']}/restablecer").status_code == 409
