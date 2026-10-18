import io

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.resultado import ResultadoHistorial
from app.services import contenido

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 32
SECCION = "primeros-pasos"


def _bitacora(ronda_id: int) -> list[tuple]:
    with SessionLocal() as db:
        consulta = (
            select(ResultadoHistorial)
            .where(ResultadoHistorial.ronda_id == ronda_id)
            .order_by(ResultadoHistorial.id)
        )
        return [
            (f.caso_id, f.usuario_email, f.estado, f.accion, f.paso) for f in db.scalars(consulta)
        ]


def _poner(cliente, ronda_id: int, caso: str, estado: str, pasos: list | None = None):
    cuerpo = {"ronda_id": ronda_id, "estado": estado, "pasos_marcados": pasos or []}
    respuesta = cliente.put(f"/api/resultados/{caso}", json=cuerpo)
    assert respuesta.status_code == 200
    return respuesta


def test_marcar_cambiar_y_limpiar_dejan_rastro(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    yo = "validador@local.test"
    _poner(validador, ronda_id, "A-GEN-01", "pendiente", [{"paso": 0, "estado": "pasa"}])
    _poner(validador, ronda_id, "A-GEN-01", "pasa", [{"paso": 0, "estado": "pasa"}])
    _poner(validador, ronda_id, "A-GEN-01", "falla", [{"paso": 0, "estado": "falla"}])
    _poner(validador, ronda_id, "A-GEN-01", "pendiente")
    _poner(validador, ronda_id, "A-GEN-01", "pendiente")
    assert _bitacora(ronda_id) == [
        ("A-GEN-01", yo, "pendiente", "paso", 0),
        ("A-GEN-01", yo, "pasa", "marcar", None),
        ("A-GEN-01", yo, "falla", "cambiar", 0),
        ("A-GEN-01", yo, "pendiente", "limpiar", 0),
    ]


def test_crear_en_pendiente_sin_pasos_tambien_se_registra(cliente_de, ronda_id) -> None:
    _poner(cliente_de("validador"), ronda_id, "A-GEN-03", "pendiente")
    assert [f[3] for f in _bitacora(ronda_id)] == ["crear"]


def _reportar(cliente, ronda_id: int, **extra):
    datos = {"ronda_id": ronda_id, "caso_id": "A-GEN-01", "obtenido": "No cargó", "paso": 0}
    datos.update(extra)
    imagenes = [("imagenes", ("captura.png", io.BytesIO(PNG), "image/png"))]
    respuesta = cliente.post("/api/fallas", data=datos, files=imagenes)
    assert respuesta.status_code == 201


def test_falla_y_no_pude_quedan_en_la_bitacora(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    _reportar(validador, ronda_id, reproducible="siempre")
    _reportar(validador, ronda_id, tipo="no_pude")
    assert [(f[2], f[3]) for f in _bitacora(ronda_id)] == [
        ("falla", "marcar"),
        ("no_pude", "cambiar"),
    ]


def test_veredicto_de_seccion_registra_solo_los_afectados(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    casos = next(s for s in contenido.obtener().respuesta.secciones if s.id == SECCION).casos
    _poner(validador, ronda_id, casos[0].id, "no_pude")
    url = f"/api/secciones/{SECCION}/resultado"
    assert validador.post(url, data={"ronda_id": ronda_id, "estado": "pasa"}).status_code == 200
    filas = _bitacora(ronda_id)
    assert filas[0][:4] == (casos[0].id, "validador@local.test", "no_pude", "marcar")
    assert [(f[0], f[2], f[3]) for f in filas[1:]] == [(c.id, "pasa", "marcar") for c in casos[1:]]


def test_borrar_la_ronda_borra_su_bitacora(cliente_de, ronda_id) -> None:
    _poner(cliente_de("validador"), ronda_id, "A-GEN-01", "pasa")
    assert cliente_de("coordinacion").delete(f"/api/rondas/{ronda_id}").status_code == 204
    assert _bitacora(ronda_id) == []


def test_cerrar_guarda_la_hora_y_reabrir_la_limpia(cliente_de, ronda_id) -> None:
    coordinacion = cliente_de("coordinacion")
    url = f"/api/rondas/{ronda_id}"
    assert coordinacion.get("/api/rondas").json()[0]["cerrada_en"] is None
    cerrada = coordinacion.patch(url, json={"abierta": False}).json()
    assert cerrada["abierta"] is False and cerrada["cerrada_en"] is not None
    renombrada = coordinacion.patch(url, json={"nombre": "Otra", "abierta": False}).json()
    assert renombrada["cerrada_en"] == cerrada["cerrada_en"]
    assert coordinacion.patch(url, json={"nombre": "Más"}).json()["cerrada_en"] is not None
    reabierta = coordinacion.patch(url, json={"abierta": True}).json()
    assert reabierta["abierta"] is True and reabierta["cerrada_en"] is None
