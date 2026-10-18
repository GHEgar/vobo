import hashlib

from tests.apoyo_proyectos import crear_proyecto


def _crear(admin, **extra):
    cuerpo = {"nombre": "Sala de juntas", **extra}
    respuesta = admin.post("/api/admin/pantallas", json=cuerpo)
    assert respuesta.status_code == 201, respuesta.text
    datos = respuesta.json()
    return datos["pantalla"], datos["enlace"].rsplit("/", 1)[1], datos["enlace"]


def _filas():
    from app.core.database import SessionLocal
    from app.models.pantalla import Pantalla

    with SessionLocal() as db:
        return [(p.id, p.token_hash, p.ultimo_uso) for p in db.query(Pantalla).all()]


def test_crud_de_pantallas(cliente_de) -> None:
    admin = cliente_de("administracion")
    pantalla, token, enlace = _crear(admin, vistas=["grafo", "general"], segundos=30)
    assert enlace == f"http://testserver/pantalla/{token}"
    assert pantalla["vistas"] == ["grafo", "general"]
    assert pantalla["segundos"] == 30 and pantalla["activa"] is True
    assert pantalla["proyectos"] == [] and pantalla["autor_email"] == "administracion@local.test"
    assert "token" not in pantalla and "token_hash" not in pantalla
    [listada] = admin.get("/api/admin/pantallas").json()
    assert listada["id"] == pantalla["id"] and "token_hash" not in listada
    cambio = admin.patch(
        f"/api/admin/pantallas/{pantalla['id']}", json={"nombre": " Pasillo ", "segundos": 60}
    )
    assert cambio.status_code == 200
    assert cambio.json()["nombre"] == "Pasillo" and cambio.json()["segundos"] == 60
    assert admin.delete(f"/api/admin/pantallas/{pantalla['id']}").status_code == 204
    assert admin.get("/api/admin/pantallas").json() == []
    assert admin.delete(f"/api/admin/pantallas/{pantalla['id']}").status_code == 404


def test_validaciones(cliente_de) -> None:
    admin = cliente_de("administracion")
    url = "/api/admin/pantallas"
    assert admin.post(url, json={"nombre": "x", "segundos": 5}).status_code == 422
    assert admin.post(url, json={"nombre": "x", "segundos": 301}).status_code == 422
    assert admin.post(url, json={"nombre": "x", "vistas": []}).status_code == 422
    assert admin.post(url, json={"nombre": "x", "vistas": ["tabla"]}).status_code == 422
    assert admin.post(url, json={"nombre": "  "}).status_code == 422
    assert admin.post(url, json={"nombre": "x", "proyectos": ["nada"]}).status_code == 422
    repetidas = admin.post(url, json={"nombre": "x", "vistas": ["general", "general"]})
    assert repetidas.json()["pantalla"]["vistas"] == ["general"]


def test_solo_administracion(cliente_de) -> None:
    coordinacion = cliente_de("coordinacion")
    assert coordinacion.get("/api/admin/pantallas").status_code == 403
    assert coordinacion.post("/api/admin/pantallas", json={"nombre": "x"}).status_code == 403
    sin_csrf = cliente_de("administracion")
    del sin_csrf.headers["X-CSRF-Token"]
    assert sin_csrf.post("/api/admin/pantallas", json={"nombre": "x"}).status_code == 403


def test_solo_se_guarda_el_hash(cliente_de) -> None:
    _, token, _ = _crear(cliente_de("administracion"))
    [(_, guardado, _)] = _filas()
    assert len(token) >= 43
    assert guardado == hashlib.sha256(token.encode()).hexdigest()
    assert guardado != token


def test_publico_sin_sesion_y_registra_uso(cliente_de) -> None:
    _, token, _ = _crear(cliente_de("administracion"), vistas=["general"], segundos=15)
    anonimo = cliente_de(None)
    respuesta = anonimo.get(f"/api/pantalla/{token}")
    assert respuesta.status_code == 200
    assert respuesta.headers["cache-control"] == "no-store"
    cuerpo = respuesta.json()
    assert cuerpo["nombre"] == "Sala de juntas"
    assert cuerpo["vistas"] == ["general"] and cuerpo["segundos"] == 15
    assert cuerpo["marca"]["producto"]
    assert anonimo.get(f"/api/pantalla/{token}/datos").status_code == 200
    [(_, _, uso)] = _filas()
    assert uso is not None


def test_token_malo_inactivo_o_regenerado_da_404(cliente_de) -> None:
    admin = cliente_de("administracion")
    pantalla, token, _ = _crear(admin)
    anonimo = cliente_de(None)
    for malo in ("x", "a" * 43, "a" * 300):
        assert anonimo.get(f"/api/pantalla/{malo}").status_code == 404
        assert anonimo.get(f"/api/pantalla/{malo}/datos").status_code == 404
    regenerada = admin.post(f"/api/admin/pantallas/{pantalla['id']}/regenerar").json()
    nuevo = regenerada["enlace"].rsplit("/", 1)[1]
    assert nuevo != token
    assert anonimo.get(f"/api/pantalla/{token}").status_code == 404
    assert anonimo.get(f"/api/pantalla/{token}/datos").status_code == 404
    assert anonimo.get(f"/api/pantalla/{nuevo}").status_code == 200
    admin.patch(f"/api/admin/pantallas/{pantalla['id']}", json={"activa": False})
    inactiva = anonimo.get(f"/api/pantalla/{nuevo}/datos")
    assert inactiva.status_code == 404
    assert inactiva.json() == {"detail": "Pantalla no encontrada"}


def test_proyectos_elegidos_y_en_orden(en_base, cliente_de) -> None:
    admin = cliente_de("administracion")
    crear_proyecto(admin)
    crear_proyecto(admin, "web", "Portal web", color_nombre="#123456")
    _, token, _ = _crear(admin, proyectos=["web", "movil"])
    datos = cliente_de(None).get(f"/api/pantalla/{token}/datos").json()
    assert [p["clave"] for p in datos["proyectos"]] == ["web", "movil"]
    colores = {p["clave"]: p["color"] for p in datos["proyectos"]}
    assert colores["web"] == "#123456"
    assert colores["movil"] in {"#D95926", "#199E70"}
    admin.patch("/api/admin/proyectos/" + str(_id_de(admin, "web")), json={"archivado": True})
    from app.services import pantalla_datos

    pantalla_datos.olvidar()
    datos = cliente_de(None).get(f"/api/pantalla/{token}/datos").json()
    assert [p["clave"] for p in datos["proyectos"]] == ["movil"]


def _id_de(admin, clave: str) -> int:
    proyectos = admin.get("/api/admin/proyectos").json()["proyectos"]
    return next(p["id"] for p in proyectos if p["clave"] == clave)
