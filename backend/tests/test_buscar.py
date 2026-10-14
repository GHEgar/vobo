URL = "/api/buscar"


def _buscar(cliente, q: str, ronda: int | None = None) -> list[dict]:
    params: dict = {"q": q}
    if ronda is not None:
        params["ronda"] = ronda
    respuesta = cliente.get(URL, params=params)
    assert respuesta.status_code == 200
    return respuesta.json()


def _ids(resultados: list[dict], tipo: str) -> list[str]:
    return [r["id"] for r in resultados if r["tipo"] == tipo]


def test_encuentra_un_paso_por_una_palabra_de_su_texto(cliente_de) -> None:
    resultados = _buscar(cliente_de("validador"), "camiza")
    paso = next(r for r in resultados if r["tipo"] == "paso")
    assert paso["id"] == "C-CAT-02:1"
    assert paso["ruta"] == "/caso/C-CAT-02?paso=1"
    assert "camiza" in paso["contexto"]
    assert set(paso) == {"tipo", "id", "titulo", "contexto", "ruta"}


def test_ignora_acentos_y_mayusculas(cliente_de) -> None:
    resultados = _buscar(cliente_de("validador"), "CATALOGO")
    assert "C-CAT-01:1" in _ids(resultados, "paso")
    assert "catalogo" in _ids(resultados, "seccion")


def test_exige_todas_las_palabras(cliente_de) -> None:
    validador = cliente_de("validador")
    con_una = _ids(_buscar(validador, "rango"), "paso")
    con_dos = _ids(_buscar(validador, "rango 300"), "paso")
    assert {"C-CAT-01:1", "B-CAT-01:1"} <= set(con_una)
    assert "C-CAT-01:1" in con_dos
    assert "B-CAT-01:1" not in con_dos


def test_minimo_de_caracteres(cliente_de) -> None:
    validador = cliente_de("validador")
    assert _buscar(validador, "c") == []
    assert _buscar(validador, "   ") == []
    assert _buscar(validador, "") == []


def test_casos_y_pasos_primero_y_titulo_antes_que_cuerpo(cliente_de) -> None:
    resultados = _buscar(cliente_de("validador"), "precio")
    tipos = [r["tipo"] for r in resultados]
    ultimo_caso = max(i for i, t in enumerate(tipos) if t in {"caso", "paso"})
    assert all(t in {"caso", "paso"} for t in tipos[: ultimo_caso + 1])
    assert resultados[0]["tipo"] == "caso"
    assert "precio" in resultados[0]["titulo"].lower()
    assert len(resultados) <= 40


def test_herramientas_y_procedimientos_llevan_a_donde_aparecen(cliente_de) -> None:
    validador = cliente_de("validador")
    herramienta = next(
        r for r in _buscar(validador, "tolera errores") if r["tipo"] == "herramienta"
    )
    assert herramienta["id"] == "busqueda-tolerante"
    assert herramienta["ruta"] == "/seccion/catalogo"
    procedimiento = next(
        r for r in _buscar(validador, "filtrar catalogo") if r["tipo"] == "procedimiento"
    )
    assert procedimiento["id"] == "filtrar-por-precio"
    assert procedimiento["ruta"] == "/caso/C-CAT-01?paso=1"


def test_contexto_corto(cliente_de) -> None:
    for resultado in _buscar(cliente_de("validador"), "tienda"):
        assert len(resultado["contexto"]) <= 122


def test_sin_acceso_tecnico_no_ve_secciones_tecnicas(cliente_de) -> None:
    consulta = "restaura base temporal"
    assert "D-RES-01:2" not in _ids(_buscar(cliente_de("validador"), consulta), "paso")
    assert "D-RES-01:2" in _ids(_buscar(cliente_de("coordinacion"), consulta), "paso")


def test_respeta_las_asignaciones_de_la_ronda(cliente_de, ronda_id) -> None:
    cliente_de("coordinacion").put(
        f"/api/rondas/{ronda_id}/asignaciones",
        json=[{"usuario_email": "validador@local.test", "seccion_id": "pedidos"}],
    )
    validador = cliente_de("validador")
    assert _buscar(validador, "camiza", ronda_id) == []
    assert "C-PED-02:2" in _ids(_buscar(validador, "preparando guarda", ronda_id), "paso")
    assert _buscar(validador, "camiza") != []


def test_requiere_sesion_y_ronda_existente(cliente_de) -> None:
    assert cliente_de(None).get(URL, params={"q": "camiza"}).status_code == 401
    assert cliente_de("validador").get(URL, params={"q": "camiza", "ronda": 999}).status_code == 404
