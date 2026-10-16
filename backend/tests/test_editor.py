import pytest

from tests.apoyo_contenido import con_resultado, seccion_nueva, versiones


@pytest.fixture
def editor(en_base, cliente_de):
    return cliente_de("administracion")


def _ids(cliente) -> list[str]:
    return [s["id"] for s in cliente.get("/api/contenido").json()["secciones"]]


@pytest.mark.parametrize(
    ("metodo", "ruta"),
    [
        ("get", "/api/editor/estado"),
        ("get", "/api/editor/secciones"),
        ("post", "/api/editor/secciones"),
        ("put", "/api/editor/secciones/catalogo"),
        ("get", "/api/editor/procedimientos"),
        ("post", "/api/editor/importar"),
        ("get", "/api/contenido/exportar.zip"),
    ],
)
def test_sin_permiso_de_edicion_recibe_403(en_base, cliente_de, metodo: str, ruta: str) -> None:
    assert getattr(cliente_de("coordinacion"), metodo)(ruta).status_code == 403
    assert getattr(cliente_de(None), metodo)(ruta).status_code == 401


def test_las_mutaciones_exigen_csrf(editor) -> None:
    editor.headers.pop("X-CSRF-Token")
    assert editor.post("/api/editor/secciones", json={"datos": seccion_nueva()}).status_code == 403


def test_administracion_ve_la_pagina_del_editor(en_base, cliente_de) -> None:
    assert "editor" in cliente_de("administracion").get("/api/auth/me").json()["usuario"]["paginas"]
    assert (
        "editor" not in cliente_de("coordinacion").get("/api/auth/me").json()["usuario"]["paginas"]
    )


def test_un_rol_propio_puede_editar(en_base, cliente_de) -> None:
    admin = cliente_de("administracion")
    rol = admin.post(
        "/api/admin/roles",
        json={
            "clave": "redaccion",
            "nombre": "Redacción",
            "permisos": ["validacion.contenido.editar"],
        },
    )
    assert rol.status_code == 201
    validador = cliente_de("validador")
    persona = next(
        p for p in admin.get("/api/admin/personas").json() if p["email"].startswith("validador")
    )
    admin.put(f"/api/admin/personas/{persona['id']}/roles", json={"roles": ["redaccion"]})
    assert validador.get("/api/editor/secciones").status_code == 200


def test_con_archivos_el_editor_no_edita(cliente_de) -> None:
    admin = cliente_de("administracion")
    estado = admin.get("/api/editor/estado").json()
    assert estado["fuente"] == "archivos"
    assert estado["editable"] is False
    assert admin.get("/api/editor/secciones").status_code == 409
    assert admin.post("/api/editor/secciones", json={"datos": seccion_nueva()}).status_code == 409


def test_crea_edita_y_borra_una_seccion(editor) -> None:
    creada = editor.post("/api/editor/secciones", json={"datos": seccion_nueva()})
    assert creada.status_code == 201
    assert creada.json()["datos"]["orden"] > 90
    assert "nueva" in _ids(editor)
    datos = {**creada.json()["datos"], "titulo": "Otro título"}
    assert editor.put("/api/editor/secciones/nueva", json={"datos": datos}).status_code == 200
    titulos = {s["id"]: s["titulo"] for s in editor.get("/api/contenido").json()["secciones"]}
    assert titulos["nueva"] == "Otro título"
    assert editor.delete("/api/editor/secciones/nueva").status_code == 204
    assert "nueva" not in _ids(editor)
    acciones = [v["accion"] for v in editor.get("/api/editor/historial/seccion/nueva").json()]
    assert acciones == ["borrar", "editar", "crear"]


def test_errores_por_campo(editor) -> None:
    datos = seccion_nueva("Mal Id")
    datos["sistema"] = "inexistente"
    datos["casos"][0]["severidad"] = "enorme"
    respuesta = editor.post("/api/editor/secciones", json={"datos": datos})
    assert respuesta.status_code == 422
    assert ["casos", 0, "severidad"] in [e["loc"] for e in respuesta.json()["detail"]]
    datos["casos"][0]["severidad"] = "media"
    datos["casos"][0]["pasos"][0]["procedimiento"] = "no-existe"
    datos["casos"][0]["herramienta"] = "otra"
    datos["casos"].append({**datos["casos"][0]})
    lugares = [
        e["loc"]
        for e in editor.post("/api/editor/secciones", json={"datos": datos}).json()["detail"]
    ]
    for esperado in (["id"], ["sistema"], ["casos", 0, "herramienta"], ["casos", 1, "id"]):
        assert esperado in lugares
    assert ["casos", 0, "pasos", 0, "procedimiento"] in lugares


def test_un_caso_de_otra_seccion_no_se_repite(editor) -> None:
    datos = seccion_nueva()
    datos["casos"][0]["id"] = "A-GEN-01"
    respuesta = editor.post("/api/editor/secciones", json={"datos": datos})
    assert respuesta.status_code == 422
    assert respuesta.json()["detail"][0]["loc"] == ["casos", 0, "id"]


def test_el_id_de_la_seccion_no_cambia(editor) -> None:
    datos = editor.get("/api/editor/secciones/catalogo").json()["datos"]
    respuesta = editor.put(
        "/api/editor/secciones/catalogo", json={"datos": {**datos, "id": "otro"}}
    )
    assert respuesta.status_code == 422


def test_casos_con_resultados_son_inmutables(editor, ronda_id) -> None:
    con_resultado(ronda_id, "A-GEN-01")
    detalle = editor.get("/api/editor/secciones/primeros-pasos").json()
    assert detalle["casos_bloqueados"] == ["A-GEN-01"]
    assert detalle["con_resultados"] is True
    datos = detalle["datos"]
    renombrado = {**datos, "casos": [{**datos["casos"][0], "id": "A-GEN-99"}, *datos["casos"][1:]]}
    respuesta = editor.put("/api/editor/secciones/primeros-pasos", json={"datos": renombrado})
    assert respuesta.status_code == 409
    assert "A-GEN-01" in respuesta.json()["detail"]
    sin_caso = {**datos, "casos": datos["casos"][1:]}
    assert (
        editor.put("/api/editor/secciones/primeros-pasos", json={"datos": sin_caso}).status_code
        == 409
    )
    titulo = {**datos, "casos": [{**datos["casos"][0], "titulo": "Nuevo"}, *datos["casos"][1:]]}
    assert (
        editor.put("/api/editor/secciones/primeros-pasos", json={"datos": titulo}).status_code
        == 200
    )


def test_seccion_con_resultados_no_se_borra_pero_se_oculta(editor, ronda_id) -> None:
    con_resultado(ronda_id, "A-GEN-01")
    assert editor.delete("/api/editor/secciones/primeros-pasos").status_code == 409
    listado = {s["id"]: s for s in editor.get("/api/editor/secciones").json()}
    assert listado["primeros-pasos"]["con_resultados"] is True
    oculta = editor.put("/api/editor/secciones/primeros-pasos/oculta", json={"oculta": True})
    assert oculta.json()["datos"]["oculta"] is True
    assert "primeros-pasos" not in _ids(editor)
    editor.put("/api/editor/secciones/primeros-pasos/oculta", json={"oculta": False})
    assert "primeros-pasos" in _ids(editor)


def test_restaura_una_version(editor) -> None:
    datos = editor.get("/api/editor/secciones/catalogo").json()["datos"]
    original = datos["titulo"]
    editor.put("/api/editor/secciones/catalogo", json={"datos": {**datos, "titulo": "Cambiado"}})
    historial = editor.get("/api/editor/historial/seccion/catalogo").json()
    assert historial[0]["accion"] == "editar"
    assert historial[0]["datos"]["titulo"] == original
    assert editor.post(f"/api/editor/historial/{historial[0]['id']}/restaurar").status_code == 204
    assert editor.get("/api/editor/secciones/catalogo").json()["datos"]["titulo"] == original
    creacion = historial[-1]
    assert creacion["datos"] is None
    assert editor.post(f"/api/editor/historial/{creacion['id']}/restaurar").status_code == 409


def test_restaura_una_seccion_borrada(editor) -> None:
    editor.delete("/api/editor/secciones/pedidos")
    borrado = editor.get("/api/editor/historial/seccion/pedidos").json()[0]
    assert editor.post(f"/api/editor/historial/{borrado['id']}/restaurar").status_code == 204
    assert "pedidos" in _ids(editor)


def test_guardar_sin_cambios_no_crea_version(editor) -> None:
    datos = editor.get("/api/editor/secciones/catalogo").json()["datos"]
    editor.put("/api/editor/secciones/catalogo", json={"datos": datos})
    antes = versiones()
    editor.put("/api/editor/secciones/catalogo", json={"datos": datos})
    assert versiones() == antes


def test_ordena_y_duplica(editor) -> None:
    ids = [s["id"] for s in editor.get("/api/editor/secciones").json()]
    invertido = list(reversed(ids))
    assert editor.put("/api/editor/secciones/orden", json={"ids": invertido}).status_code == 204
    assert _ids(editor) == invertido
    assert editor.put("/api/editor/secciones/orden", json={"ids": ids[:1]}).status_code == 422
    copia = editor.post("/api/editor/secciones/catalogo/duplicar", json={"id": "catalogo-2"})
    assert copia.status_code == 201
    casos = [c["id"] for c in copia.json()["datos"]["casos"]]
    assert all(c.endswith("-COPIA") for c in casos)
    assert copia.json()["datos"]["titulo"].endswith("(copia)")


def test_el_listado_incluye_audiencia_y_secciones_ocultas(editor) -> None:
    datos = seccion_nueva("tecnica-nueva", audiencia="tecnica")
    assert editor.post("/api/editor/secciones", json={"datos": datos}).status_code == 201
    editor.put("/api/editor/secciones/tecnica-nueva/oculta", json={"oculta": True})
    listado = {s["id"]: s for s in editor.get("/api/editor/secciones").json()}
    assert listado["tecnica-nueva"]["audiencia"] == "tecnica"
    assert listado["tecnica-nueva"]["oculta"] is True
    assert listado["catalogo"]["audiencia"] == "funcional"
    assert "tecnica-nueva" not in _ids(editor)
