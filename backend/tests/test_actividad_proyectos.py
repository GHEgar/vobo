import pytest

from tests.apoyo_proyectos import crear_proyecto, importar, marcar, paquete_movil, ronda


@pytest.fixture
def admin(en_base, cliente_de):
    return cliente_de("administracion")


def test_cada_proyecto_ve_su_actividad(admin, cliente_de) -> None:
    crear_proyecto(admin)
    importar(admin, "movil", paquete_movil(admin))
    principal = ronda(admin, "Ronda principal")
    movil = ronda(admin, "Ronda móvil", "movil")
    validador = cliente_de("validador")
    assert marcar(validador, principal, "A-GEN-01").status_code == 200
    assert marcar(validador, movil, "M-APP-01", "falla").status_code == 200
    de_principal = admin.get("/api/actividad?tipo=resultado").json()["eventos"]
    assert [e["caso_id"] for e in de_principal] == ["A-GEN-01"]
    assert de_principal[0]["ruta"] == "/caso/A-GEN-01"
    del_movil = admin.get("/api/actividad?tipo=resultado&proyecto=movil").json()["eventos"]
    assert [e["caso_id"] for e in del_movil] == ["M-APP-01"]
    assert del_movil[0]["ruta"] == "/caso/M-APP-01?proyecto=movil"
    assert del_movil[0]["caso_titulo"] == "Abrir la aplicación móvil"
    assert del_movil[0]["resumen"] == "Marcó Falla"
    contenido = admin.get("/api/actividad?tipo=contenido&proyecto=movil").json()["eventos"]
    assert contenido and all(
        e["usuario"]["email"] == "administracion@local.test" for e in contenido
    )
    assert all(set(e) >= {"resumen", "estado"} for e in contenido)
    assert not any("datos" in e for e in contenido)


def test_sin_contenido_en_base_no_hay_eventos_de_contenido(cliente_de) -> None:
    eventos = cliente_de("coordinacion").get("/api/actividad?tipo=contenido").json()["eventos"]
    assert eventos == []
