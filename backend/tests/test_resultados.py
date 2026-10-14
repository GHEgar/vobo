from app.core.database import SessionLocal
from app.models.resultado import Resultado


def test_resultado_se_actualiza_sin_duplicarse(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    url = "/api/resultados/A-GEN-01"
    primero = validador.put(
        url, json={"ronda_id": ronda_id, "estado": "pendiente", "pasos_marcados": [0]}
    )
    assert primero.status_code == 200
    segundo = validador.put(
        url, json={"ronda_id": ronda_id, "estado": "pasa", "pasos_marcados": [0, 0, 9]}
    )
    assert segundo.status_code == 200
    assert segundo.json()["estado"] == "pasa"
    assert segundo.json()["pasos_marcados"] == [{"paso": 0, "estado": "pasa", "comentario": None}]
    with SessionLocal() as db:
        assert db.query(Resultado).count() == 1
    mis = validador.get(f"/api/mis-casos?ronda={ronda_id}").json()
    assert [r["caso_id"] for r in mis["resultados"]] == ["A-GEN-01"]


def test_caso_inexistente_da_404(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    respuesta = validador.put(
        "/api/resultados/NO-EXISTE", json={"ronda_id": ronda_id, "estado": "pasa"}
    )
    assert respuesta.status_code == 404


def test_ronda_cerrada_da_409(cliente_de, ronda_id) -> None:
    coordinacion = cliente_de("coordinacion")
    assert coordinacion.patch(f"/api/rondas/{ronda_id}", json={"abierta": False}).status_code == 200
    validador = cliente_de("validador")
    respuesta = validador.put(
        "/api/resultados/A-GEN-01", json={"ronda_id": ronda_id, "estado": "pasa"}
    )
    assert respuesta.status_code == 409


def test_sin_csrf_se_rechaza(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    del validador.headers["X-CSRF-Token"]
    respuesta = validador.put(
        "/api/resultados/A-GEN-01", json={"ronda_id": ronda_id, "estado": "pasa"}
    )
    assert respuesta.status_code == 403


def test_pasos_con_estado_y_comentario(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    pasos = [
        {"paso": 1, "estado": "comentario", "comentario": "  Tardó en cargar  "},
        {"paso": 0, "estado": "pasa"},
        {"paso": 7, "estado": "falla"},
    ]
    respuesta = validador.put(
        "/api/resultados/A-GEN-03",
        json={"ronda_id": ronda_id, "estado": "pasa", "pasos_marcados": pasos},
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["pasos_marcados"] == [
        {"paso": 0, "estado": "pasa", "comentario": None},
        {"paso": 1, "estado": "comentario", "comentario": "Tardó en cargar"},
    ]
    largo = {"paso": 0, "estado": "comentario", "comentario": "x" * 1001}
    rechazo = validador.put(
        "/api/resultados/A-GEN-03",
        json={"ronda_id": ronda_id, "estado": "pasa", "pasos_marcados": [largo]},
    )
    assert rechazo.status_code == 422


def test_filas_legadas_con_enteros_se_leen_como_pasa(cliente_de, ronda_id) -> None:
    with SessionLocal() as db:
        db.add(
            Resultado(
                ronda_id=ronda_id,
                caso_id="A-GEN-03",
                usuario_email="validador@local.test",
                estado="pendiente",
                pasos_marcados=[0, 1],
            )
        )
        db.commit()
    mis = cliente_de("validador").get(f"/api/mis-casos?ronda={ronda_id}").json()
    assert mis["resultados"][0]["pasos_marcados"] == [
        {"paso": 0, "estado": "pasa", "comentario": None},
        {"paso": 1, "estado": "pasa", "comentario": None},
    ]


def test_comentarios_llegan_a_coordinacion(cliente_de, ronda_id) -> None:
    from tests.conftest import TOKEN_LECTURA

    validador = cliente_de("validador")
    validador.put(
        "/api/resultados/A-GEN-03",
        json={
            "ronda_id": ronda_id,
            "estado": "pendiente",
            "pasos_marcados": [{"paso": 0, "estado": "comentario", "comentario": "Lento"}],
        },
    )
    validador.put(
        "/api/resultados/A-GEN-01",
        json={"ronda_id": ronda_id, "estado": "no_pude", "comentario": "Sin red"},
    )
    assert validador.get("/api/comentarios").status_code == 403
    cabecera = {"Authorization": f"Bearer {TOKEN_LECTURA}"}
    lista = cliente_de(None).get(f"/api/comentarios?ronda={ronda_id}", headers=cabecera).json()
    assert {(c["caso_id"], c["tipo"], c["comentario"]) for c in lista} == {
        ("A-GEN-03", "paso", "Lento"),
        ("A-GEN-01", "no_pude", "Sin red"),
    }


def test_comentarios_del_caso_propios_o_de_todos(cliente_de, ronda_id) -> None:
    plantilla = "Qué hice: entré\nQué vi: lento\nQué esperaba: rápido\n" + "x" * 900
    for clave in ("validador", "coordinacion"):
        cliente = cliente_de(clave)
        cliente.put(
            "/api/resultados/A-GEN-03",
            json={
                "ronda_id": ronda_id,
                "estado": "pendiente",
                "pasos_marcados": [{"paso": 0, "estado": "comentario", "comentario": plantilla}],
            },
        )
    validador = cliente_de("validador")
    propios = validador.get(f"/api/comentarios/caso/A-GEN-03?ronda={ronda_id}").json()
    assert [c["usuario_email"] for c in propios] == ["validador@local.test"]
    assert propios[0]["autor"] == "Valeria Validadora"
    assert propios[0]["ronda_nombre"] == "Ronda 1"
    assert propios[0]["comentario"] == plantilla.strip()
    todos = cliente_de("coordinacion").get(f"/api/comentarios/caso/A-GEN-03?ronda={ronda_id}")
    assert len(todos.json()) == 2
