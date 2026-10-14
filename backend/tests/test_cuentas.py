from pathlib import Path

import pytest

from app.core.config import settings
from tests.conftest import TOKEN_LECTURA

ARCHIVO = """# cuentas de prueba

val-admin-01@tienda.ejemplo=Secreta#1=con-igual
val-cliente-01@tienda.ejemplo = otra
val-raro-01@tienda.ejemplo=x
linea-sin-formato
"""


@pytest.fixture
def archivo_cuentas(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    ruta = tmp_path / "validacion_cuentas"
    ruta.write_text(ARCHIVO, encoding="utf-8")
    monkeypatch.setattr(settings, "cuentas_path", str(ruta))
    return ruta


def test_lista_las_cuentas_a_un_usuario_con_sesion(cliente_de, archivo_cuentas) -> None:
    respuesta = cliente_de("sin-rol").get("/api/cuentas-prueba")
    assert respuesta.status_code == 200
    assert respuesta.headers["cache-control"] == "no-store"
    assert respuesta.json() == [
        {
            "email": "val-admin-01@tienda.ejemplo",
            "password": "Secreta#1=con-igual",
            "descripcion": "Administración de la tienda",
        },
        {
            "email": "val-cliente-01@tienda.ejemplo",
            "password": "otra",
            "descripcion": "Cliente con compras previas",
        },
        {"email": "val-raro-01@tienda.ejemplo", "password": "x", "descripcion": "Cuenta de prueba"},
    ]


def test_sin_sesion_da_401(cliente_de, archivo_cuentas) -> None:
    assert cliente_de(None).get("/api/cuentas-prueba").status_code == 401


def test_el_token_de_lectura_no_sirve(cliente_de, archivo_cuentas) -> None:
    cabecera = {"Authorization": f"Bearer {TOKEN_LECTURA}"}
    assert cliente_de(None).get("/api/cuentas-prueba", headers=cabecera).status_code == 401


def test_sin_archivo_devuelve_lista_vacia(cliente_de, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "cuentas_path", str(tmp_path / "no-existe"))
    assert cliente_de("validador").get("/api/cuentas-prueba").json() == []


def test_solo_ve_las_cuentas_de_sus_secciones(cliente_de, ronda_id, archivo_cuentas) -> None:
    coordinacion = cliente_de("coordinacion")
    validador = cliente_de("validador")
    email = validador.get("/api/auth/me").json()["usuario"]["email"]
    asignar = coordinacion.put(
        f"/api/rondas/{ronda_id}/asignaciones",
        json=[{"usuario_email": email, "seccion_id": "catalogo"}],
    )
    assert asignar.status_code == 200
    correos = [c["email"] for c in validador.get(f"/api/cuentas-prueba?ronda={ronda_id}").json()]
    assert correos == ["val-cliente-01@tienda.ejemplo"]
    assert "val-admin-01@tienda.ejemplo" not in correos
    todas = coordinacion.get(f"/api/cuentas-prueba?ronda={ronda_id}").json()
    assert len(todas) == 3


def test_sin_asignaciones_ve_todo_lo_funcional(cliente_de, ronda_id, archivo_cuentas) -> None:
    respuesta = cliente_de("validador").get(f"/api/cuentas-prueba?ronda={ronda_id}")
    correos = [c["email"] for c in respuesta.json()]
    assert "val-admin-01@tienda.ejemplo" in correos
    assert "val-raro-01@tienda.ejemplo" not in correos


def test_las_descripciones_salen_de_la_instancia(tmp_path, monkeypatch) -> None:
    from app.services import cuentas

    (tmp_path / "secciones").mkdir()
    (tmp_path / "instancia.yaml").write_text(
        "cuentas:\n  - prefijo: VAL-Ops\n    descripcion: Operación\n", encoding="utf-8"
    )
    monkeypatch.setattr(settings, "contenido_dir", str(tmp_path))
    assert cuentas.descripcion_de("val-ops-02@x.test") == "Operación"
    assert cuentas.descripcion_de("val-admin-01@x.test") == "Cuenta de prueba"
