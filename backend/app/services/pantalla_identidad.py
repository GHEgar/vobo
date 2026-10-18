import hashlib
import hmac

from app.core.config import settings

PALETA_PROYECTOS = ("#3987E5", "#D95926", "#199E70", "#C98500", "#D55181", "#9085E9")
PALETA_PERSONAS = (
    "#6250D6",
    "#C2417A",
    "#0E7C86",
    "#8A5A00",
    "#2F6FB0",
    "#7A4FB5",
    "#9C4F2A",
    "#4D6B8A",
)
ANONIMO = "Alguien"


def color_de_proyecto(propio: str | None, posicion: int) -> str:
    return propio or PALETA_PROYECTOS[posicion % len(PALETA_PROYECTOS)]


def _resumen(email: str) -> bytes:
    clave = settings.secret_key.encode()
    return hmac.new(clave, f"pantalla:{email.lower()}".encode(), hashlib.sha256).digest()


def id_de_persona(email: str) -> str:
    return _resumen(email).hex()[:16]


def color_de_persona(email: str) -> str:
    return PALETA_PERSONAS[_resumen(email)[0] % len(PALETA_PERSONAS)]


def _palabras(nombre: str) -> list[str]:
    return [p for p in (nombre or "").split() if "@" not in p]


def nombre_de_pila(nombre: str) -> str:
    palabras = _palabras(nombre)
    return palabras[0][:30] if palabras else ANONIMO


def iniciales(nombre: str) -> str:
    palabras = _palabras(nombre)
    if not palabras:
        return "?"
    letras = [p[0] for p in palabras[:2]]
    return "".join(letras).upper()
