import shutil
from pathlib import Path

from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.services import contenido, contenido_base, contenido_editor
from app.services.contenido_importacion import importar_inicial
from tests.apoyo_contenido import WEBP, principal, seccion_nueva, sin_version, versiones
from tests.conftest import CONTENIDO


def _serializado(actual: contenido.Contenido) -> dict:
    return {
        "respuesta": sin_version(actual.respuesta.model_dump(mode="json")),
        "casos": sorted(actual.casos),
        "herramientas": sorted(actual.herramientas),
        "instancia": actual.instancia.model_dump(mode="json"),
    }


def test_la_fuente_por_omision_es_archivos() -> None:
    assert settings.contenido_fuente == "archivos"
    assert contenido.cargar() is contenido.cargar(CONTENIDO)


def test_importa_al_arrancar_y_da_el_mismo_contenido(en_base, cliente_de) -> None:
    cliente_de(None)
    assert _serializado(contenido.cargar()) == _serializado(contenido.cargar(CONTENIDO))
    assert versiones() > 0
    validador = cliente_de("validador")
    respuesta = validador.get("/api/contenido").json()
    esperado = contenido.cargar(CONTENIDO).respuesta.model_dump(mode="json")
    assert sin_version(respuesta) == esperado


def test_la_media_importada_conserva_la_url(en_base, tmp_path: Path, monkeypatch) -> None:
    raiz = tmp_path / "contenido"
    shutil.copytree(CONTENIDO, raiz)
    (raiz / "media").mkdir()
    (raiz / "media" / "usar-esta-pagina.webp").write_bytes(WEBP)
    (raiz / "media" / "notas.txt").write_text("no es media", encoding="utf-8")
    monkeypatch.setattr(settings, "contenido_dir", str(raiz))
    assert importar_inicial(engine)
    assert (en_base / "usar-esta-pagina.webp").read_bytes() == WEBP
    assert _serializado(contenido.cargar()) == _serializado(contenido.cargar(raiz))


def test_no_reimporta_si_ya_hubo_cambios(en_base) -> None:
    assert importar_inicial(engine)
    antes = versiones()
    with SessionLocal() as db:
        for seccion in ("catalogo", "pedidos"):
            fila = contenido_editor.seccion_o_404(db, principal(db), seccion)
            contenido_editor.borrar(db, fila, "a@x.test")
    assert not importar_inicial(engine)
    assert versiones() == antes + 2


def test_sin_contenido_en_disco_no_importa_nada(en_base, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "contenido_dir", str(tmp_path / "vacio"))
    assert not importar_inicial(engine)
    assert contenido.cargar().respuesta.secciones == []


def test_dos_procesos_recargan_con_la_marca_de_la_base(en_base) -> None:
    importar_inicial(engine)
    uno = contenido_base.CacheDeBase()
    otro = contenido_base.CacheDeBase()
    primero = uno.obtener()
    assert otro.obtener() is not primero
    assert uno.obtener() is primero
    with SessionLocal() as db:
        contenido_editor.crear(db, principal(db), seccion_nueva(), "a@x.test")
    assert any(s.id == "nueva" for s in otro.obtener().respuesta.secciones)
    recargado = uno.obtener()
    assert recargado is not primero
    assert any(s.id == "nueva" for s in recargado.respuesta.secciones)


def test_una_seccion_rota_en_la_base_se_reporta(en_base) -> None:
    importar_inicial(engine)
    with SessionLocal() as db:
        fila = contenido_editor.seccion_o_404(db, principal(db), "catalogo")
        fila.datos = {**fila.datos, "casos": "roto"}
        db.commit()
    contenido_base.cache.olvidar()
    actual = contenido.cargar()
    assert any(e.startswith("catalogo:") for e in actual.respuesta.errores)
    assert all(s.id != "catalogo" for s in actual.respuesta.secciones)
