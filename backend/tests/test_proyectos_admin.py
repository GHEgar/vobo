import pytest

from app.core.database import SessionLocal
from app.services import proyectos
from tests.apoyo_proyectos import crear_proyecto, ronda

RUTA = "/api/admin/proyectos"


@pytest.fixture
def admin(cliente_de):
    return cliente_de("administracion")


def test_en_modo_archivos_hay_un_solo_proyecto(admin) -> None:
    estado = admin.get(RUTA).json()
    assert estado["fuente"] == "archivos"
    assert not estado["multiples"]
    assert "CONTENIDO_FUENTE=base" in estado["motivo"]
    assert [p["clave"] for p in estado["proyectos"]] == ["principal"]
    rechazo = admin.post(RUTA, json={"clave": "otro", "nombre": "Otro"})
    assert rechazo.status_code == 409
    assert "para varios proyectos usa CONTENIDO_FUENTE=base" in rechazo.json()["detail"]
    unico = estado["proyectos"][0]["id"]
    cambio = admin.patch(
        f"{RUTA}/{unico}", json={"nombre": "Release 2.0", "color_nombre": "#123abc"}
    )
    assert cambio.json()["nombre"] == "Release 2.0"
    assert cambio.json()["color_nombre"] == "#123ABC"


def test_permisos(cliente_de) -> None:
    assert cliente_de(None).get("/api/proyectos").status_code == 401
    validador = cliente_de("validador")
    assert [p["clave"] for p in validador.get("/api/proyectos").json()] == ["principal"]
    assert validador.get(RUTA).status_code == 403
    assert validador.post(RUTA, json={"clave": "x", "nombre": "X"}).status_code == 403
    assert cliente_de("coordinacion").patch(f"{RUTA}/1", json={"nombre": "X"}).status_code == 403


def test_crear_ordenar_archivar_y_marcar(en_base, admin) -> None:
    movil = crear_proyecto(admin, descripcion="La app")
    web = crear_proyecto(admin, "web", "Sitio web")
    assert admin.post(RUTA, json={"clave": "web", "nombre": "Repetido"}).status_code == 409
    assert admin.post(RUTA, json={"clave": "Con Espacio", "nombre": "X"}).status_code == 422
    assert (
        admin.post(RUTA, json={"clave": "x", "nombre": "X", "color_nombre": "rojo"}).status_code
        == 422
    )
    estado = admin.get(RUTA).json()["proyectos"]
    ids = [p["id"] for p in estado]
    assert admin.put(f"{RUTA}/orden", json={"ids": list(reversed(ids))}).status_code == 204
    assert [p["clave"] for p in admin.get("/api/proyectos").json()] == ["web", "movil", "principal"]
    assert admin.put(f"{RUTA}/orden", json={"ids": ids[:1]}).status_code == 422

    assert admin.patch(f"{RUTA}/{web['id']}", json={"archivado": True}).status_code == 200
    assert "web" not in [p["clave"] for p in admin.get("/api/proyectos").json()]
    assert admin.post("/api/rondas", json={"nombre": "R", "proyecto": "web"}).status_code == 409
    assert admin.patch(f"{RUTA}/{web['id']}", json={"por_omision": True}).status_code == 409
    assert admin.patch(f"{RUTA}/{web['id']}", json={"archivado": False}).status_code == 200

    principal = next(p for p in estado if p["clave"] == "principal")
    assert admin.patch(f"{RUTA}/{principal['id']}", json={"archivado": True}).status_code == 409
    assert admin.patch(f"{RUTA}/{principal['id']}", json={"por_omision": False}).status_code == 409
    assert admin.patch(f"{RUTA}/{movil['id']}", json={"por_omision": True}).status_code == 200
    with SessionLocal() as db:
        assert proyectos.por_omision(db).clave == "movil"
    assert admin.get("/api/rondas").json() == []
    assert admin.get("/api/instancia").json()["proyecto"]["clave"] == "movil"


def test_borrar_solo_sin_rondas(en_base, admin) -> None:
    movil = crear_proyecto(admin)
    web = crear_proyecto(admin, "web", "Sitio web")
    ronda(admin, "R1", "movil")
    assert admin.delete(f"{RUTA}/{movil['id']}").status_code == 409
    assert admin.delete(f"{RUTA}/{web['id']}").status_code == 204
    principal = next(p for p in admin.get(RUTA).json()["proyectos"] if p["por_omision"])
    assert admin.delete(f"{RUTA}/{principal['id']}").status_code == 409
    conteos = {p["clave"]: p["rondas"] for p in admin.get(RUTA).json()["proyectos"]}
    assert conteos == {"principal": 0, "movil": 1}


def test_resolucion_ronda_parametro_omision(en_base, admin) -> None:
    crear_proyecto(admin)
    movil = ronda(admin, "R movil", "movil")
    principal = ronda(admin, "R principal")
    with SessionLocal() as db:
        assert proyectos.resolver(db, movil, "principal").clave == "movil"
        assert proyectos.resolver(db, principal, "movil").clave == "principal"
        assert proyectos.resolver(db, None, "movil").clave == "movil"
        assert proyectos.resolver(db, None, None).clave == "principal"
        assert proyectos.resolver(db, 9999, "movil").clave == "movil"
    assert admin.get("/api/rondas?proyecto=nada").status_code == 404
