import csv
import io

from tests.conftest import TOKEN_LECTURA


def _reportar(cliente, ronda_id, caso_id, obtenido, tipo="falla") -> dict:
    datos = {"ronda_id": ronda_id, "caso_id": caso_id, "obtenido": obtenido, "tipo": tipo}
    if tipo == "falla":
        datos["reproducible"] = "siempre"
    respuesta = cliente.post("/api/fallas", data=datos)
    assert respuesta.status_code == 201
    return respuesta.json()


def _filas(respuesta) -> list[dict]:
    texto = respuesta.content.decode("utf-8")
    assert texto.startswith("﻿")
    return list(csv.DictReader(io.StringIO(texto[1:])))


def test_columnas_bom_y_archivo(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    falla = _reportar(validador, ronda_id, "C-CAT-01", "El filtro no filtra")
    respuesta = cliente_de("coordinacion").get(
        f"/api/fallas/informe.csv?ronda={ronda_id}&tz=America/Mexico_City"
    )
    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"].startswith("text/csv")
    disposicion = respuesta.headers["content-disposition"]
    assert disposicion.startswith(f'attachment; filename="fallas-ronda-{ronda_id}-')
    assert disposicion.endswith('.csv"')
    [fila] = _filas(respuesta)
    assert list(fila)[:4] == ["id", "ronda", "caso", "título del caso"]
    assert fila["id"] == str(falla["id"])
    assert fila["ronda"] == "Ronda 1"
    assert fila["título del caso"] == falla["caso_titulo"]
    assert fila["sección"] == "Catálogo y búsqueda"
    assert fila["herramienta"] == "Filtro por rango de precio"
    assert fila["severidad"] == "Alta"
    assert fila["estado"] == "Nueva"
    assert fila["reproducible"] == "Siempre"
    assert fila["reportó"] == "Valeria Validadora"
    assert fila["correo"] == "validador@local.test"
    assert fila["paso"] == "Fuera de los pasos"
    assert fila["capturas"] == "0"
    assert len(fila["fecha"]) == 16


def test_filtros_como_el_listado(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    _reportar(validador, ronda_id, "C-CAT-01", "Falla alta")
    _reportar(validador, ronda_id, "A-GEN-01", "Falla crítica")
    _reportar(validador, ronda_id, "C-CAT-02", "No tuve datos", tipo="no_pude")
    coordinacion = cliente_de("coordinacion")
    for consulta, esperados in (
        ("severidad=critica", {"A-GEN-01"}),
        ("sistema=catalogo", {"C-CAT-01", "C-CAT-02"}),
        ("tipo=no_pude", {"C-CAT-02"}),
        ("estado=cerrada", set()),
    ):
        url = f"/api/fallas/informe.csv?ronda={ronda_id}&{consulta}"
        casos = {f["caso"] for f in _filas(coordinacion.get(url))}
        lista = coordinacion.get(f"/api/fallas?ronda={ronda_id}&{consulta}").json()
        assert casos == esperados == {f["caso_id"] for f in lista}
    assert coordinacion.get("/api/fallas/informe.csv?severidad=otra").status_code == 422


def test_token_de_lectura_descarga(cliente_de, ronda_id) -> None:
    _reportar(cliente_de("validador"), ronda_id, "C-CAT-01", "Algo")
    cabecera = {"Authorization": f"Bearer {TOKEN_LECTURA}"}
    respuesta = cliente_de(None).get("/api/fallas/informe.csv", headers=cabecera)
    assert respuesta.status_code == 200
    assert 'filename="fallas-' in respuesta.headers["content-disposition"]
    assert len(_filas(respuesta)) == 1


def test_permiso_como_listar(cliente_de) -> None:
    assert cliente_de("validador").get("/api/fallas/informe.csv").status_code == 403
    assert cliente_de(None).get("/api/fallas/informe.csv").status_code == 401
    malo = {"Authorization": "Bearer otro"}
    assert cliente_de(None).get("/api/fallas/informe.csv", headers=malo).status_code == 401


def test_escapa_formulas(cliente_de, ronda_id) -> None:
    validador = cliente_de("validador")
    for texto in ('=HYPERLINK("x")', "+1+1", "-2+3", "@SUM(A1)", "Texto normal"):
        _reportar(validador, ronda_id, "C-CAT-01", texto)
    filas = _filas(cliente_de("coordinacion").get("/api/fallas/informe.csv"))
    obtenidos = {f["obtenido"] for f in filas}
    assert obtenidos == {
        '\'=HYPERLINK("x")',
        "'+1+1",
        "'-2+3",
        "'@SUM(A1)",
        "Texto normal",
    }
