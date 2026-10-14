import os
import shutil
from pathlib import Path

from app.services import contenido
from tests.conftest import CONTENIDO


def test_carga_el_contenido_de_ejemplo() -> None:
    actual = contenido.cargar(CONTENIDO)
    ids = [s.id for s in actual.respuesta.secciones]
    assert "primeros-pasos" in ids
    caso = actual.casos["A-GEN-01"]
    assert caso.seccion_id == "primeros-pasos"
    assert caso.caso.severidad == "critica"
    assert all(len(u.caso.pasos) > 0 for u in actual.casos.values())


def test_el_contenido_de_ejemplo_no_tiene_errores() -> None:
    actual = contenido.cargar(CONTENIDO)
    assert actual.respuesta.errores == []


def test_media_ausente_queda_sin_url(tmp_path: Path) -> None:
    shutil.copytree(CONTENIDO / "secciones", tmp_path / "secciones")
    (tmp_path / "media").mkdir()
    sin_media = contenido.cargar(tmp_path)
    primeros = next(s for s in sin_media.respuesta.secciones if s.id == "primeros-pasos")
    assert all(m.url is None for m in primeros.media)
    (tmp_path / "media" / "usar-esta-pagina.webp").write_bytes(b"RIFF0000WEBP")
    con_media = contenido.cargar(tmp_path)
    primeros = next(s for s in con_media.respuesta.secciones if s.id == "primeros-pasos")
    assert primeros.media[0].url == "/media/usar-esta-pagina.webp"


def test_recarga_cuando_cambia_el_archivo(tmp_path: Path) -> None:
    shutil.copytree(CONTENIDO / "secciones", tmp_path / "secciones")
    primero = contenido.cargar(tmp_path)
    assert contenido.cargar(tmp_path) is primero
    archivo = tmp_path / "secciones" / "10-primeros-pasos.yaml"
    texto = archivo.read_text(encoding="utf-8").replace("Primeros pasos", "Primeros pasos bis", 1)
    archivo.write_text(texto, encoding="utf-8")
    os.utime(archivo, ns=(1, archivo.stat().st_mtime_ns + 10_000_000))
    recargado = contenido.cargar(tmp_path)
    assert recargado is not primero
    assert any(s.titulo == "Primeros pasos bis" for s in recargado.respuesta.secciones)


def test_procedimientos_aceptan_lista_o_mapa(tmp_path: Path) -> None:
    (tmp_path / "secciones").mkdir()
    (tmp_path / "procedimientos.yaml").write_text(
        "- id: entrar-a-la-tienda\n  titulo: Entrar a la tienda\n", encoding="utf-8"
    )
    (tmp_path / "procedimientos-extra.yaml").write_text(
        "procedimientos:\n  ventana-incognito:\n    titulo: Incógnito\n", encoding="utf-8"
    )
    ids = {p.id for p in contenido.cargar(tmp_path).respuesta.procedimientos}
    assert ids == {"entrar-a-la-tienda", "ventana-incognito"}


def test_un_archivo_roto_no_tumba_el_resto(tmp_path: Path) -> None:
    shutil.copytree(CONTENIDO / "secciones", tmp_path / "secciones")
    (tmp_path / "secciones" / "00-roto.yaml").write_text("id: [roto\n", encoding="utf-8")
    actual = contenido.cargar(tmp_path)
    assert any(e.startswith("00-roto.yaml") for e in actual.respuesta.errores)
    assert any(s.id == "primeros-pasos" for s in actual.respuesta.secciones)
