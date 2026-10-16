import pytest

from app.core.config import settings
from tests.apoyo_proyectos import (
    crear_proyecto,
    importar,
    marcar,
    paquete_movil,
    reportar,
    ronda,
)
from tests.conftest import TOKEN_LECTURA


@pytest.fixture
def admin(en_base, cliente_de):
    return cliente_de("administracion")


@pytest.fixture
def dos(admin) -> dict:
    crear_proyecto(admin, color_nombre="#aa3300")
    importar(admin, "movil", paquete_movil(admin))
    return {
        "principal": ronda(admin, "Ronda principal"),
        "movil": ronda(admin, "Ronda móvil", "movil"),
    }


def _secciones(cliente, sufijo: str = "") -> list[str]:
    return sorted(s["id"] for s in cliente.get(f"/api/contenido{sufijo}").json()["secciones"])


def test_cada_proyecto_tiene_su_contenido(admin, dos) -> None:
    principal = _secciones(admin)
    movil = _secciones(admin, "?proyecto=movil")
    assert "pedidos" in principal and "solo-movil" not in principal
    assert movil == ["catalogo", "solo-movil"]
    assert _secciones(admin, f"?ronda={dos['movil']}") == movil
    assert _secciones(admin, f"?ronda={dos['principal']}&proyecto=movil") == principal
    assert admin.get("/api/contenido?proyecto=no-existe").status_code == 404


def test_rondas_por_proyecto(admin, dos) -> None:
    assert [r["id"] for r in admin.get("/api/rondas").json()] == [dos["principal"]]
    movil = admin.get("/api/rondas?proyecto=movil").json()
    assert [r["id"] for r in movil] == [dos["movil"]]
    assert movil[0]["proyecto_id"] != admin.get("/api/rondas").json()[0]["proyecto_id"]


def test_una_ronda_no_recibe_casos_de_otro_proyecto(admin, cliente_de, dos) -> None:
    validador = cliente_de("validador")
    assert marcar(validador, dos["movil"], "M-APP-01").status_code == 200
    assert marcar(validador, dos["principal"], "M-APP-01").status_code == 404
    assert marcar(validador, dos["movil"], "A-GEN-01").status_code == 404
    assert reportar(validador, dos["principal"], "M-APP-01", "No abre").status_code == 404
    seccion = {"ronda_id": dos["principal"], "estado": "pasa"}
    assert validador.post("/api/secciones/solo-movil/resultado", data=seccion).status_code == 404


def test_el_mismo_caso_en_dos_proyectos_no_se_mezcla(admin, cliente_de, dos) -> None:
    validador = cliente_de("validador")
    assert marcar(validador, dos["movil"], "C-CAT-01", "falla").status_code == 200
    assert reportar(validador, dos["movil"], "C-CAT-01", "El filtro falla").status_code == 201
    assert marcar(validador, dos["principal"], "C-CAT-01").status_code == 200
    movil = admin.get(f"/api/tablero?ronda={dos['movil']}").json()
    principal = admin.get(f"/api/tablero?ronda={dos['principal']}").json()
    assert movil["casos_total"] == 4
    assert principal["casos_total"] > movil["casos_total"]
    assert movil["casos_ejecutados"] == principal["casos_ejecutados"] == 1
    assert [f["ronda_id"] for f in admin.get("/api/fallas?proyecto=movil").json()] == [dos["movil"]]
    assert admin.get("/api/fallas").json() == []
    assert admin.get(f"/api/fallas?ronda={dos['principal']}").json() == []
    herramientas = {h["id"] for h in admin.get(f"/api/herramientas?ronda={dos['movil']}").json()}
    assert "app-movil" in herramientas


def test_la_busqueda_respeta_el_proyecto(admin, dos) -> None:
    def ids(sufijo: str) -> set[str]:
        return {r["id"] for r in admin.get(f"/api/buscar?q=aplicacion{sufijo}").json()}

    assert "solo-movil" in ids("&proyecto=movil")
    assert "solo-movil" in ids(f"&ronda={dos['movil']}")
    assert "solo-movil" not in ids("")
    assert "solo-movil" not in ids(f"&ronda={dos['principal']}&proyecto=movil")


def test_el_token_de_lectura_usa_el_proyecto_por_omision(cliente_de, dos) -> None:
    token = cliente_de(None)
    token.headers["Authorization"] = f"Bearer {TOKEN_LECTURA}"
    assert token.get(f"/api/tablero?ronda={dos['movil']}").status_code == 200
    assert token.get("/api/fallas").status_code == 200
    zip_movil = token.get("/api/contenido/exportar.zip?proyecto=movil")
    assert zip_movil.headers["content-disposition"].endswith('contenido-movil.zip"')


def test_el_editor_trabaja_sobre_el_proyecto(admin, dos) -> None:
    estado = admin.get("/api/editor/estado?proyecto=movil").json()
    assert estado["proyecto"]["clave"] == "movil"
    assert estado["sistemas"] == estado["proyectos"]
    ids = sorted(s["id"] for s in admin.get("/api/editor/secciones?proyecto=movil").json())
    assert ids == ["catalogo", "solo-movil"]
    assert admin.get("/api/editor/secciones/solo-movil").status_code == 404
    borrado = admin.delete("/api/editor/secciones/catalogo?proyecto=movil")
    assert borrado.status_code == 204
    assert "catalogo" in _secciones(admin)
    historial = admin.get("/api/editor/historial/seccion/catalogo?proyecto=movil").json()
    assert historial[0]["accion"] == "borrar"
    otra = admin.post(f"/api/editor/historial/{historial[0]['id']}/restaurar")
    assert otra.status_code == 404


def test_la_media_de_otro_proyecto_va_en_su_carpeta(admin, dos, en_base) -> None:
    from tests.apoyo_contenido import WEBP

    archivo = {"archivo": ("a.webp", WEBP, "image/webp")}
    ruta = "/api/editor/procedimientos/entrar-a-la-tienda/media?proyecto=movil"
    respuesta = admin.put(ruta, files=archivo)
    assert respuesta.status_code == 200
    assert respuesta.json()["media"]["url"].startswith("/media/movil/entrar-a-la-tienda.webp")
    assert (en_base / "movil" / "entrar-a-la-tienda.webp").read_bytes() == WEBP
    assert not (en_base / "entrar-a-la-tienda.webp").exists()


def test_instancia_publica_da_nombre_y_color_del_proyecto(cliente_de, dos) -> None:
    publico = cliente_de(None)
    movil = publico.get("/api/instancia?proyecto=movil").json()["proyecto"]
    assert movil == {
        "clave": "movil",
        "nombre": "App móvil",
        "color_nombre": "#AA3300",
        "por_omision": False,
    }
    assert publico.get("/api/instancia?proyecto=otro").json()["proyecto"]["clave"] == "principal"


def test_avisos_de_una_falla_llevan_su_proyecto(admin, cliente_de, dos) -> None:
    validador = cliente_de("validador")
    falla = reportar(validador, dos["movil"], "M-APP-01", "No abre").json()
    creado = admin.post("/api/avisos", json={"mensaje": "Listo", "falla_id": falla["id"]})
    assert creado.status_code == 201
    assert validador.get("/api/avisos").json()[0]["proyecto_clave"] == "movil"


def test_presencia_por_proyecto(admin, cliente_de, dos) -> None:
    validador = cliente_de("validador")
    datos = {"ruta": "/caso/M-APP-01", "caso_id": "M-APP-01", "ronda_id": dos["movil"]}
    assert validador.post("/api/presencia", json=datos).status_code == 204
    movil = admin.get("/api/presencia?proyecto=movil").json()
    assert [p["caso_titulo"] for p in movil if not p["yo"]] == ["Abrir la aplicación móvil"]
    assert all(p["yo"] for p in admin.get("/api/presencia").json())


def test_comentarios_sin_ronda_son_del_proyecto(admin, cliente_de, dos) -> None:
    validador = cliente_de("validador")
    pasos = [{"paso": 0, "estado": "falla", "comentario": "En móvil no"}]
    cuerpo = {"ronda_id": dos["movil"], "estado": "falla", "pasos_marcados": pasos}
    assert validador.put("/api/resultados/M-APP-01", json=cuerpo).status_code == 200
    assert admin.get("/api/comentarios").json() == []
    assert [c["caso_id"] for c in admin.get("/api/comentarios?proyecto=movil").json()] == [
        "M-APP-01"
    ]
    assert settings.contenido_en_base
