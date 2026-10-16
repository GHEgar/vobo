from datetime import timedelta

from tests.conftest import TOKEN_LECTURA


def _envejecer(email: str, minutos: float) -> None:
    from app.core.database import SessionLocal
    from app.core.time import utcnow
    from app.models.presencia import Presencia

    with SessionLocal() as db:
        fila = db.get(Presencia, email)
        fila.actualizado = utcnow() - timedelta(minutes=minutos)
        db.commit()


def test_upsert_una_fila_por_persona(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    primero = {"ruta": "/", "accion": "viendo"}
    assert validador.post("/api/presencia", json=primero).status_code == 204
    segundo = {
        "ruta": "/caso/A-GEN-01",
        "caso_id": "A-GEN-01",
        "paso": 2,
        "accion": "reportando",
        "ronda_id": ronda_id,
    }
    assert validador.post("/api/presencia", json=segundo).status_code == 204
    lista = cliente_de("coordinacion").get("/api/presencia").json()
    filas = [p for p in lista if p["email"] == "validador@local.test"]
    assert len(filas) == 1
    fila = filas[0]
    assert fila["nombre"] == "Valeria Validadora"
    assert fila["accion"] == "reportando"
    assert fila["paso"] == 2
    assert fila["ronda_id"] == ronda_id
    assert fila["caso_titulo"] == "Entras a la tienda con tu cuenta de prueba"
    assert fila["seccion_id"] == "primeros-pasos"
    assert fila["seccion_titulo"] == "Primeros pasos"
    assert fila["pasos_total"] >= 1
    assert fila["estado"] == "activo"
    assert fila["yo"] is False


def test_solicitante_aparece_marcado(cliente_de) -> None:
    coordinacion = cliente_de("coordinacion")
    datos = {"ruta": "/seccion/catalogo", "seccion_id": "catalogo", "accion": "viendo"}
    coordinacion.post("/api/presencia", json=datos)
    [fila] = coordinacion.get("/api/presencia").json()
    assert fila["yo"] is True
    assert fila["seccion_titulo"] == "Catálogo y búsqueda"
    assert fila["caso_titulo"] == ""


def test_ventana_y_estados(cliente_de) -> None:
    for clave in ("validador", "aprobacion", "sin-rol"):
        cliente_de(clave).post("/api/presencia", json={"ruta": "/", "accion": "viendo"})
    _envejecer("aprobacion@local.test", 5)
    _envejecer("sinrol@local.test", 11)
    lista = cliente_de("coordinacion").get("/api/presencia").json()
    estados = {p["email"]: p["estado"] for p in lista}
    assert estados == {"validador@local.test": "activo", "aprobacion@local.test": "inactivo"}
    assert [p["email"] for p in lista] == ["validador@local.test", "aprobacion@local.test"]
    inactivo = next(p for p in lista if p["estado"] == "inactivo")
    assert 290 <= inactivo["hace_segundos"] <= 310


def test_validador_no_lista(cliente_de) -> None:
    validador = cliente_de("validador")
    assert validador.get("/api/presencia").status_code == 403
    assert cliente_de("aprobacion").get("/api/presencia").status_code == 403
    assert cliente_de(None).get("/api/presencia").status_code == 401


def test_token_de_lectura_no_registra_ni_lista(cliente_de) -> None:
    anonimo = cliente_de(None)
    cabecera = {"Authorization": f"Bearer {TOKEN_LECTURA}"}
    respuesta = anonimo.post("/api/presencia", json={"ruta": "/"}, headers=cabecera)
    assert respuesta.status_code == 401
    assert anonimo.get("/api/presencia", headers=cabecera).status_code == 401
    assert cliente_de("coordinacion").get("/api/presencia").json() == []


def test_valida_datos(cliente_de) -> None:
    validador = cliente_de("validador")
    malos = (
        {"ruta": "/", "accion": "borrando"},
        {"ruta": "/" + "x" * 300},
        {"ruta": ""},
        {"ruta": "/", "paso": 0},
        {"ruta": "/", "caso_id": "c" * 61},
    )
    for datos in malos:
        assert validador.post("/api/presencia", json=datos).status_code == 422


def test_exige_csrf_y_origen(cliente_de) -> None:
    validador = cliente_de("validador")
    origen = {"Origin": "http://otro.ejemplo"}
    respuesta = validador.post("/api/presencia", json={"ruta": "/"}, headers=origen)
    assert respuesta.status_code == 403
    del validador.headers["X-CSRF-Token"]
    assert validador.post("/api/presencia", json={"ruta": "/"}).status_code == 403
    assert cliente_de("coordinacion").get("/api/presencia").json() == []


def test_envios_simultaneos_no_fallan(cliente_de) -> None:
    from concurrent.futures import ThreadPoolExecutor

    validador = cliente_de("validador")
    with ThreadPoolExecutor(max_workers=6) as grupo:
        codigos = list(
            grupo.map(
                lambda _: validador.post("/api/presencia", json={"ruta": "/"}).status_code,
                range(12),
            )
        )
    assert set(codigos) == {204}
    assert len(cliente_de("coordinacion").get("/api/presencia").json()) == 1


IPHONE = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 26_0 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1"
)


def _desde(email: str):
    from app.core.database import SessionLocal
    from app.core.time import como_utc
    from app.models.presencia import Presencia

    with SessionLocal() as db:
        return como_utc(db.get(Presencia, email).desde)


def _mover_desde(email: str, minutos: float) -> None:
    from app.core.database import SessionLocal
    from app.core.time import utcnow
    from app.models.presencia import Presencia

    with SessionLocal() as db:
        db.get(Presencia, email).desde = utcnow() - timedelta(minutes=minutos)
        db.commit()


def test_navegador_dispositivo_y_pantalla(cliente_de) -> None:
    validador = cliente_de("validador")
    cabecera = {"User-Agent": IPHONE}
    datos = {"ruta": "/", "pantalla": "390x844"}
    assert validador.post("/api/presencia", json=datos, headers=cabecera).status_code == 204
    lista = cliente_de("coordinacion").get("/api/presencia").json()
    [fila] = [p for p in lista if p["email"] == "validador@local.test"]
    assert fila["navegador"] == "Safari 26"
    assert fila["dispositivo"] == "movil"
    assert fila["pantalla"] == "390x844"
    assert fila["desde"] is not None
    assert "agente" not in fila


def test_pantalla_invalida(cliente_de) -> None:
    validador = cliente_de("validador")
    for pantalla in ("390", "0x844", "390×844", "a" * 12, "99999x1x2"):
        datos = {"ruta": "/", "pantalla": pantalla}
        assert validador.post("/api/presencia", json=datos).status_code == 422


def test_desde_se_conserva_y_se_reinicia(cliente_de) -> None:
    validador = cliente_de("validador")
    email = "validador@local.test"
    validador.post("/api/presencia", json={"ruta": "/"})
    _mover_desde(email, 30)
    _envejecer(email, 3)
    validador.post("/api/presencia", json={"ruta": "/tablero"})
    [fila] = [
        p for p in cliente_de("coordinacion").get("/api/presencia").json() if p["yo"] is False
    ]
    assert 1790 <= fila["sesion_segundos"] <= 1810
    _envejecer(email, 11)
    validador.post("/api/presencia", json={"ruta": "/"})
    assert _desde(email) is not None
    [fila] = [
        p for p in cliente_de("coordinacion").get("/api/presencia").json() if p["yo"] is False
    ]
    assert fila["sesion_segundos"] < 5
