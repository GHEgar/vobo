import re
from dataclasses import dataclass

LARGO_AGENTE = 300

NAVEGADORES: tuple[tuple[str, str], ...] = (
    (r"EdgA?/(\d+)", "Edge"),
    (r"EdgiOS/(\d+)", "Edge"),
    (r"OPR/(\d+)", "Opera"),
    (r"SamsungBrowser/(\d+)", "Samsung Internet"),
    (r"FxiOS/(\d+)", "Firefox"),
    (r"Firefox/(\d+)", "Firefox"),
    (r"CriOS/(\d+)", "Chrome"),
    (r"Chrome/(\d+)", "Chrome"),
    (r"Version/(\d+)[\d.]*.*Safari/", "Safari"),
)

TABLETA = re.compile(r"iPad|Tablet|PlayBook|Silk|Kindle")
MOVIL = re.compile(r"Mobi|iPhone|iPod|Android|Windows Phone")


@dataclass(frozen=True)
class Agente:
    navegador: str
    dispositivo: str
    crudo: str


def _navegador(ua: str) -> str:
    for patron, nombre in NAVEGADORES:
        coincide = re.search(patron, ua)
        if coincide:
            return f"{nombre} {coincide.group(1)}"
    return ""


def _dispositivo(ua: str) -> str:
    if TABLETA.search(ua) or ("Android" in ua and "Mobile" not in ua):
        return "tableta"
    if MOVIL.search(ua):
        return "movil"
    return "escritorio"


def describir(ua: str | None) -> Agente:
    texto = (ua or "").strip()
    return Agente(
        navegador=_navegador(texto), dispositivo=_dispositivo(texto), crudo=texto[:LARGO_AGENTE]
    )
