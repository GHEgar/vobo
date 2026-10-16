import io
import json
from datetime import timedelta

from tests.conftest import TOKEN_LECTURA


def _actividad(cliente, **params):
    respuesta = cliente.get("/api/actividad", params=params)
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()


def _sembrar(cliente_de, ronda_id: int) -> dict:
    validador = cliente_de("validador")
    pasos = [
        {"paso": 0, "estado": "pasa"},
        {"paso": 1, "estado": "comentario", "comentario": "Tardó en cargar"},
    ]
    respuesta = validador.put(
        "/api/resultados/A-GEN-03",
        json={"ronda_id": ronda_id, "estado": "pasa", "pasos_marcados": pasos},
    )
    assert respuesta.status_code == 200
    imagen = io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"0" * 32)
    falla = validador.post(
        "/api/fallas",
        data={
            "ronda_id": ronda_id,
            "caso_id": "C-CAT-01",
            "obtenido": "No cargó",
            "reproducible": "siempre",
            "severidad": "alta",
            "paso": 0,
        },
        files=[("imagenes", ("captura.png", imagen, "image/png"))],
    )
    assert falla.status_code == 201
    coordinacion = cliente_de("coordinacion")
    aviso = coordinacion.post(
        "/api/avisos",
        json={
            "destinatarios": ["validador@local.test", "aprobacion@local.test"],
            "mensaje": "Mañana abre la ronda",
        },
    )
    assert aviso.status_code == 201
    return {"validador": validador, "coordinacion": coordinacion, "falla": falla.json()}


def test_solo_coordinacion_y_administracion(cliente_de) -> None:
    for clave in ("validador", "aprobacion", "sin-rol"):
        cliente = cliente_de(clave)
        assert cliente.get("/api/actividad").status_code == 403
        assert cliente.get("/api/actividad/resumen").status_code == 403
    anonimo = cliente_de(None)
    assert anonimo.get("/api/actividad").status_code == 401
    cabecera = {"Authorization": f"Bearer {TOKEN_LECTURA}"}
    assert anonimo.get("/api/actividad", headers=cabecera).status_code == 401
    for clave in ("coordinacion", "administracion"):
        assert cliente_de(clave).get("/api/actividad").status_code == 200


def test_eventos_derivados_y_ordenados(cliente_de, ronda_id) -> None:
    _sembrar(cliente_de, ronda_id)
    pagina = _actividad(cliente_de("coordinacion"))
    eventos = pagina["eventos"]
    tipos = {e["tipo"] for e in eventos}
    assert {"resultado", "comentario", "falla", "aviso", "sesion"} <= tipos
    momentos = [(e["cuando"], e["id"]) for e in eventos]
    assert momentos == sorted(momentos, reverse=True)
    resultado = next(e for e in eventos if e["tipo"] == "resultado" and e["caso_id"] == "A-GEN-03")
    assert resultado["estado"] == "pasa"
    assert resultado["resumen"] == "Marcó Pasa"
    assert resultado["paso"] == 2
    assert resultado["ruta"] == "/caso/A-GEN-03?paso=2"
    assert resultado["usuario"] == {"email": "validador@local.test", "nombre": "Valeria Validadora"}
    assert resultado["caso_titulo"] == "Una segunda cuenta en incógnito no cierra la primera"
    comentario = next(e for e in eventos if e["tipo"] == "comentario")
    assert comentario["comentario"] == "Tardó en cargar"
    assert comentario["paso"] == 2
    assert comentario["aproximado"] is True
    falla = next(e for e in eventos if e["tipo"] == "falla")
    assert falla["severidad"] == "alta"
    assert falla["capturas"] == 1
    assert falla["paso"] == 1
    [aviso] = [e for e in eventos if e["tipo"] == "aviso"]
    assert aviso["resumen"].startswith("Envió el aviso «")
    assert aviso["resumen"].endswith("a 2 personas")
    assert pagina["siguiente"] is None


def test_no_expone_datos_sensibles(cliente_de, ronda_id) -> None:
    from sqlalchemy import select

    from app.core.database import SessionLocal
    from app.models.falla import Evidencia
    from app.models.usuario import Sesion

    datos = _sembrar(cliente_de, ronda_id)
    texto = json.dumps(_actividad(cliente_de("coordinacion")))
    with SessionLocal() as db:
        sesiones = list(db.scalars(select(Sesion)))
        rutas = [e.ruta for e in db.scalars(select(Evidencia))]
    assert sesiones and rutas
    for sesion in sesiones:
        assert sesion.id not in texto
        if len(sesion.access_token) >= 16:
            assert sesion.access_token not in texto
    for ruta in rutas:
        assert ruta not in texto
    assert datos["validador"].headers["X-CSRF-Token"] not in texto
    for prohibido in ("token", "contrasena", "hash", "imagenes", "evidencias", "navegador"):
        assert f'"{prohibido}' not in texto


def test_filtros_por_persona_y_tipo(cliente_de, ronda_id) -> None:
    _sembrar(cliente_de, ronda_id)
    coordinacion = cliente_de("coordinacion")
    propios = _actividad(coordinacion, usuario="validador@local.test")["eventos"]
    assert propios and {e["usuario"]["email"] for e in propios} == {"validador@local.test"}
    solo = _actividad(coordinacion, tipo="falla,comentario")["eventos"]
    assert {e["tipo"] for e in solo} == {"falla", "comentario"}
    assert coordinacion.get("/api/actividad", params={"tipo": "borrado"}).status_code == 422
    de_ronda = _actividad(coordinacion, ronda=ronda_id)["eventos"]
    assert de_ronda and all(e["ronda_id"] == ronda_id for e in de_ronda if e["tipo"] != "aviso")
    assert not [e for e in de_ronda if e["tipo"] == "sesion"]


def test_cursor_recorre_sin_repetir(cliente_de, ronda_id) -> None:
    _sembrar(cliente_de, ronda_id)
    coordinacion = cliente_de("coordinacion")
    completo = [e["id"] for e in _actividad(coordinacion)["eventos"]]
    vistos: list[str] = []
    antes = None
    while True:
        params = {"limite": 2, **({"antes": antes} if antes else {})}
        pagina = _actividad(coordinacion, **params)
        assert len(pagina["eventos"]) <= 2
        vistos.extend(e["id"] for e in pagina["eventos"])
        antes = pagina["siguiente"]
        if antes is None:
            break
    assert vistos == completo
    assert len(set(vistos)) == len(vistos)
    assert coordinacion.get("/api/actividad", params={"limite": 101}).status_code == 422
    assert coordinacion.get("/api/actividad", params={"antes": "ayer|x"}).status_code == 422


def test_empates_en_el_mismo_instante(cliente_de, ronda_id) -> None:
    from app.core.database import SessionLocal
    from app.core.time import utcnow
    from app.models.aprobacion import Aprobacion

    instante = utcnow() - timedelta(minutes=1)
    with SessionLocal() as db:
        for _ in range(5):
            db.add(
                Aprobacion(
                    ronda_id=ronda_id,
                    tipo="caracteristica",
                    objetivo_id="A-GEN-01",
                    estado="aprobada",
                    usuario_email="aprobacion@local.test",
                    usuario_nombre="Ana",
                    creada=instante,
                )
            )
        db.commit()
    coordinacion = cliente_de("coordinacion")
    vistos: list[str] = []
    antes = None
    while True:
        params = {"limite": 2, "tipo": "aprobacion", **({"antes": antes} if antes else {})}
        pagina = _actividad(coordinacion, **params)
        vistos.extend(e["id"] for e in pagina["eventos"])
        antes = pagina["siguiente"]
        if antes is None:
            break
    assert len(vistos) == len(set(vistos)) == 5


def test_decision_y_aprobacion(cliente_de, ronda_id) -> None:
    coordinacion = cliente_de("coordinacion")
    herramienta = coordinacion.get(f"/api/herramientas?ronda={ronda_id}").json()[0]["id"]
    coordinacion.put(
        f"/api/decisiones/{herramienta}",
        json={"ronda_id": ronda_id, "decision": "aplazar", "motivo": "Falta probar"},
    )
    cliente_de("aprobacion").post(
        "/api/aprobaciones",
        json={
            "ronda_id": ronda_id,
            "items": [{"tipo": "herramienta", "objetivo_id": herramienta, "estado": "rechazada"}],
        },
    )
    eventos = _actividad(coordinacion, tipo="decision,aprobacion")["eventos"]
    decision = next(e for e in eventos if e["tipo"] == "decision")
    assert decision["resumen"].startswith("Decidió aplazar")
    assert decision["comentario"] == "Falta probar"
    assert decision["ruta"] == "/herramientas"
    aprobacion = next(e for e in eventos if e["tipo"] == "aprobacion")
    assert aprobacion["estado"] == "rechazada"
    assert aprobacion["usuario"]["nombre"] == "Ana Aprobadora"


def test_resumen_cuenta_activos_e_inactivos(cliente_de) -> None:
    from tests.test_presencia import _envejecer

    for clave in ("validador", "aprobacion"):
        cliente_de(clave).post("/api/presencia", json={"ruta": "/"})
    _envejecer("aprobacion@local.test", 5)
    resumen = cliente_de("coordinacion").get("/api/actividad/resumen").json()
    assert resumen == {"activos": 1, "inactivos": 1}
