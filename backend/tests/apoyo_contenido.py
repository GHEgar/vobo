import io
import re
import zipfile

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.contenido import ContenidoVersion
from app.models.resultado import Resultado
from app.services import proyectos

WEBP = b"RIFF\x24\x00\x00\x00WEBPVP8 " + b"\x00" * 24
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 24
MP4 = b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 24


def principal(db: Session) -> int:
    return proyectos.por_omision(db).id


def sin_version(datos: object) -> object:
    if isinstance(datos, dict):
        return {k: sin_version(v) for k, v in datos.items()}
    if isinstance(datos, list):
        return [sin_version(v) for v in datos]
    if isinstance(datos, str):
        return re.sub(r"\?v=\d+$", "", datos)
    return datos


def versiones() -> int:
    with SessionLocal() as db:
        return db.query(ContenidoVersion).count()


def con_resultado(ronda_id: int, caso_id: str) -> None:
    with SessionLocal() as db:
        db.add(
            Resultado(ronda_id=ronda_id, caso_id=caso_id, usuario_email="v@x.test", estado="pasa")
        )
        db.commit()


def leer_zip(contenido: bytes) -> dict[str, bytes]:
    with zipfile.ZipFile(io.BytesIO(contenido)) as archivo:
        return {n: archivo.read(n) for n in archivo.namelist()}


def armar_zip(entradas: dict[str, bytes]) -> bytes:
    salida = io.BytesIO()
    with zipfile.ZipFile(salida, "w") as archivo:
        for nombre, contenido in entradas.items():
            archivo.writestr(nombre, contenido)
    return salida.getvalue()


def seccion_nueva(seccion_id: str = "nueva", **extra: object) -> dict:
    return {
        "id": seccion_id,
        "titulo": "Sección nueva",
        "sistema": "catalogo",
        "herramientas": [{"id": "general", "nombre": "General", "hoy": "prod"}],
        "casos": [
            {
                "id": f"N-{seccion_id.upper()}-01",
                "familia": "A",
                "titulo": "Un caso",
                "pasos": [{"texto": "Hacer algo", "procedimiento": "entrar-a-la-tienda"}],
                "esperado": "Pasa algo",
                "severidad": "media",
            }
        ],
        **extra,
    }
