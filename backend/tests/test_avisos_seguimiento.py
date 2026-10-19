from datetime import date

from app.core.database import SessionLocal
from app.models.aviso import Aviso
from app.services import avisos_seguimiento, fallas
from tests.test_informe_fallas import _reportar
from tests.test_seguimiento import _comentar, _comentarios

COORDINACION = "coordinacion@local.test"
VALIDADOR = "validador@local.test"


def _avisos(cliente) -> list[dict]:
    return cliente.get("/api/avisos").json()


def test_respuesta_a_falla_avisa_a_quien_reporto(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    falla = _reportar(validador, ronda_id, "C-CAT-01", "No filtra")
    coordinacion = cliente_de("coordinacion")
    url = f"/api/fallas/{falla['id']}"
    coordinacion.patch(url, json={"plazo": "2026-11-05"})
    assert _avisos(validador) == []
    assert coordinacion.post(f"{url}/respuestas", json={"texto": "Lo reviso"}).status_code == 201
    [aviso] = _avisos(validador)
    assert aviso["titulo"] == "Respuesta a tu reporte de C-CAT-01"
    assert aviso["mensaje"] == "Lo reviso\n\nPlazo: 5 de noviembre de 2026"
    assert aviso["falla_id"] == falla["id"] and aviso["caso_id"] == "C-CAT-01"
    assert aviso["proyecto_clave"] is not None
    assert aviso["autor_email"] == COORDINACION
    assert aviso["autor_nombre"] == "Carlos Coordinación"
    assert _avisos(coordinacion) == []


def test_estados_de_falla_avisan_con_plantilla(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    falla = _reportar(validador, ronda_id, "C-CAT-01", "No filtra")
    coordinacion = cliente_de("coordinacion")
    url = f"/api/fallas/{falla['id']}"
    coordinacion.patch(url, json={"estado": "en_curso"})
    coordinacion.patch(url, json={"estado": "lista_para_revalidar"})
    coordinacion.patch(url, json={"estado": "cerrada", "nota_resolucion": "Corregido en 2.1"})
    coordinacion.patch(url, json={"estado": "nueva"})
    avisos = sorted(_avisos(validador), key=lambda a: a["id"])
    assert [(a["titulo"], a["mensaje"]) for a in avisos] == [
        (
            "Estamos trabajando en tu reporte de C-CAT-01",
            "Estamos trabajando en tu reporte de C-CAT-01.",
        ),
        ("Ya puedes volver a probar C-CAT-01", "Ya puedes volver a probar C-CAT-01."),
        (
            "Tu reporte de C-CAT-01 fue atendido",
            "Tu reporte de C-CAT-01 ya fue atendido.\n\nNota de resolución: Corregido en 2.1",
        ),
    ]
    assert all(a["falla_id"] == falla["id"] for a in avisos)


def test_estado_y_plazo_juntos_dan_un_aviso(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    falla = _reportar(validador, ronda_id, "C-CAT-01", "No filtra")
    coordinacion = cliente_de("coordinacion")
    cambios = {"estado": "en_curso", "plazo": "2026-12-01"}
    assert coordinacion.patch(f"/api/fallas/{falla['id']}", json=cambios).status_code == 200
    [aviso] = _avisos(validador)
    assert aviso["mensaje"].endswith("\n\nPlazo: 1 de diciembre de 2026")
    coordinacion.patch(f"/api/fallas/{falla['id']}", json={"estado": "en_curso"})
    assert len(_avisos(validador)) == 1


def test_sin_aviso_a_uno_mismo(cliente_de, ronda_id) -> None:
    coordinacion = cliente_de("coordinacion")
    falla = _reportar(coordinacion, ronda_id, "C-CAT-01", "No filtra")
    url = f"/api/fallas/{falla['id']}"
    coordinacion.patch(url, json={"estado": "cerrada"})
    coordinacion.post(f"{url}/respuestas", json={"texto": "Listo"})
    assert _avisos(coordinacion) == []


def test_comentario_avisa_por_estado_y_respuesta(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    _comentar(validador, ronda_id, "C-CAT-01", "El botón no se ve")
    coordinacion = cliente_de("coordinacion")
    [comentario] = _comentarios(coordinacion, ronda_id)
    url = f"/api/comentarios/{comentario['id']}"
    coordinacion.patch(url, json={"estado": "en_curso"})
    coordinacion.post(f"{url}/respuestas", json={"texto": "Ya lo vimos"})
    coordinacion.patch(url, json={"estado": "resuelto", "plazo": "2026-11-05"})
    coordinacion.patch(url, json={"estado": "nuevo"})
    avisos = sorted(_avisos(validador), key=lambda a: a["id"])
    assert [a["titulo"] for a in avisos] == [
        "Estamos trabajando en tu comentario en C-CAT-01",
        "Respuesta a tu comentario en C-CAT-01",
        "Tu comentario en C-CAT-01 fue atendido",
    ]
    assert avisos[1]["mensaje"] == "Ya lo vimos"
    assert avisos[2]["mensaje"].endswith("Plazo: 5 de noviembre de 2026")
    assert all(a["falla_id"] is None and a["caso_id"] == "C-CAT-01" for a in avisos)
    assert all(a["proyecto_clave"] is not None for a in avisos)


def test_sin_permiso_no_hay_aviso(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    falla = _reportar(cliente_de("coordinacion"), ronda_id, "C-CAT-01", "No filtra")
    url = f"/api/fallas/{falla['id']}"
    assert validador.patch(url, json={"estado": "cerrada"}).status_code == 403
    assert validador.post(f"{url}/respuestas", json={"texto": "Hola"}).status_code == 403
    assert _avisos(cliente_de("coordinacion")) == []


def test_funciones_publicas_fuera_de_la_api(cliente_de, ronda_id) -> None:
    falla = _reportar(cliente_de("validador"), ronda_id, "C-CAT-01", "No filtra")
    with SessionLocal() as db:
        fila = fallas.obtener_o_404(db, falla["id"])
        fila.estado = "lista_para_revalidar"
        fila.plazo = date(2026, 3, 9)
        aviso = avisos_seguimiento.avisar_estado(db, "falla", fila, COORDINACION)
        assert aviso is not None
        assert avisos_seguimiento.avisar_respuesta(db, "falla", fila, VALIDADOR, "x") is None
        db.commit()
        guardado = db.get(Aviso, aviso.id)
        assert (
            guardado.mensaje == "Ya puedes volver a probar C-CAT-01.\n\nPlazo: 9 de marzo de 2026"
        )
        assert guardado.usuario_email == VALIDADOR
