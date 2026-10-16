import pytest

from app.services import contenido, cuentas, instancia

RUTA = "/api/admin/configuracion"


@pytest.fixture
def admin(cliente_de):
    return cliente_de("administracion")


def test_sin_configuracion_la_instancia_queda_igual_que_con_archivos(cliente_de) -> None:
    publico = cliente_de(None)
    esperada = instancia.respuesta(contenido.cargar().instancia).model_dump()
    obtenida = publico.get("/api/instancia").json()
    assert obtenida.pop("proyecto")["clave"] == "principal"
    assert obtenida == {k: v for k, v in esperada.items() if k != "proyecto"}
    hoja = publico.get("/api/instancia/tema.css")
    assert hoja.status_code == 200
    assert hoja.headers["content-type"].startswith("text/css")
    assert hoja.text == ""


def test_lo_guardado_gana_sobre_los_archivos_y_se_restablece(admin, cliente_de) -> None:
    cambios = {
        "producto": "Revisión",
        "nombre": "Equipo norte",
        "entrada": {"titulo": "Hola", "mensaje": "Entra"},
        "color_tema": "#112233",
        "logo_alt": "Marca propia",
    }
    assert admin.put(RUTA, json=cambios).status_code == 200
    publico = cliente_de(None).get("/api/instancia").json()
    assert publico["producto"] == "Revisión"
    assert publico["nombre"] == "Equipo norte"
    assert publico["descripcion"].startswith("Validación del nuevo ciclo")
    assert publico["entrada"] == {"titulo": "Hola", "mensaje": "Entra"}
    assert publico["color_tema"] == "#112233"
    assert publico["logo"]["claro"] == "/tema/logo.svg"
    assert publico["logo"]["alt"] == "Marca propia"
    estado = admin.delete(f"{RUTA}/nombre").json()
    assert "nombre" not in estado["guardada"]
    assert estado["archivos"]["nombre"] == "Tienda en línea"
    assert cliente_de(None).get("/api/instancia").json()["nombre"] == "Tienda en línea"


def test_colores_y_fuente_generan_la_hoja(admin, cliente_de) -> None:
    cambios = {"colores": {"primario": "#aa0000", "exito": "#00AA00"}, "fuente": "sistema"}
    estado = admin.put(RUTA, json=cambios).json()
    assert estado["colores"] == {"primario": "#AA0000", "exito": "#00AA00"}
    hoja = cliente_de(None).get("/api/instancia/tema.css").text
    assert "--color-primario: #AA0000;" in hoja
    assert "--color-exito: #00AA00;" in hoja
    assert "--tipo-regular: system-ui, sans-serif;" in hoja
    admin.put(RUTA, json={"colores": {"exito": "#00AA00"}, "fuente": "producto"})
    hoja = cliente_de(None).get("/api/instancia/tema.css").text
    assert "--color-primario" not in hoja
    assert "'Rotulo'" in hoja
    admin.delete(f"{RUTA}/colores")
    admin.delete(f"{RUTA}/fuente")
    assert cliente_de(None).get("/api/instancia/tema.css").text == ""


def test_el_color_del_nombre_se_edita_como_los_demas(admin, cliente_de) -> None:
    estado = admin.get(RUTA).json()
    assert "nombre" in estado["tokens"]
    assert estado["archivos"]["colores"] == {}
    assert admin.put(RUTA, json={"colores": {"nombre": "#0a0b0c"}}).status_code == 200
    hoja = cliente_de(None).get("/api/instancia/tema.css").text
    assert "--color-nombre: #0A0B0C;" in hoja
    admin.delete(f"{RUTA}/colores")
    assert "--color-nombre" not in cliente_de(None).get("/api/instancia/tema.css").text


@pytest.mark.parametrize(
    "cambios",
    [
        {"colores": {"primario": "rojo"}},
        {"colores": {"primario": "#12345"}},
        {"colores": {"sombra": "#123456"}},
        {"colores": {"nombre": "naranja"}},
        {"color_nombre": "#123456"},
        {"color_tema": "#GGGGGG"},
        {"producto": "   "},
        {"fuente": "comic"},
        {"desconocido": 1},
        {"proyectos": [{"clave": "Con Espacio", "nombre": "x"}]},
        {"proyectos": [{"clave": "a", "nombre": "A"}, {"clave": "a", "nombre": "B"}]},
        {"proyectos": [{"clave": "a", "nombre": " "}]},
        {"cuentas": [{"prefijo": "", "descripcion": "x"}]},
        {"producto": None},
    ],
)
def test_valida_los_cambios(admin, cambios: dict) -> None:
    assert admin.put(RUTA, json=cambios).status_code == 422


def test_campo_desconocido_al_restablecer_es_404(admin) -> None:
    assert admin.delete(f"{RUTA}/inventado").status_code == 404


@pytest.mark.parametrize(
    ("metodo", "ruta"),
    [
        ("get", RUTA),
        ("put", RUTA),
        ("delete", f"{RUTA}/nombre"),
        ("put", f"{RUTA}/marca/favicon"),
        ("delete", f"{RUTA}/marca/favicon"),
    ],
)
def test_solo_administracion(cliente_de, metodo: str, ruta: str) -> None:
    assert getattr(cliente_de("coordinacion"), metodo)(ruta).status_code == 403
    assert getattr(cliente_de(None), metodo)(ruta).status_code == 401


def test_exige_csrf(admin) -> None:
    del admin.headers["X-CSRF-Token"]
    assert admin.put(RUTA, json={"nombre": "x"}).status_code == 403
    assert admin.get(RUTA).status_code == 200


def test_no_quita_proyectos_que_usan_secciones(admin, cliente_de) -> None:
    estado = admin.get(RUTA).json()
    assert "general" in estado["proyectos_en_uso"]
    proyectos = [p for p in estado["archivos"]["proyectos"] if p["clave"] != "general"]
    respuesta = admin.put(RUTA, json={"proyectos": proyectos})
    assert respuesta.status_code == 409
    assert "general" in respuesta.json()["detail"]
    reordenados = [*reversed(estado["archivos"]["proyectos"]), {"clave": "nuevo", "nombre": "N"}]
    assert admin.put(RUTA, json={"proyectos": reordenados}).status_code == 200
    publico = cliente_de(None).get("/api/instancia").json()
    assert [p["clave"] for p in publico["proyectos"]][-2:] == ["general", "nuevo"]
    assert admin.get("/api/editor/estado").json()["proyectos"] == publico["proyectos"]
    assert admin.delete(f"{RUTA}/proyectos").status_code == 200


def test_las_cuentas_de_prueba_toman_la_descripcion_guardada(admin) -> None:
    assert cuentas.descripcion_de("val-admin@x.test") == "Administración de la tienda"
    nuevas = [{"prefijo": "val-admin", "descripcion": "Quien administra"}]
    assert admin.put(RUTA, json={"cuentas": nuevas}).status_code == 200
    assert cuentas.descripcion_de("val-admin@x.test") == "Quien administra"
    assert cuentas.descripcion_de("val-cliente@x.test") == cuentas.DESCRIPCION_GENERICA
