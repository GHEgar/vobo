import pytest

from app.services.agente import describir

CHROME_WIN = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
)
EDGE = f"{CHROME_WIN} Edg/141.0.3537.57"
FIREFOX = "Mozilla/5.0 (X11; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0"
SAFARI_MAC = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/26.0 Safari/605.1.15"
)
IPHONE = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 26_0 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1"
)
IPHONE_CHROME = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 26_0 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) CriOS/141.0.7390.41 Mobile/15E148 Safari/604.1"
)
ANDROID = (
    "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36"
)
SAMSUNG = (
    "Mozilla/5.0 (Linux; Android 14; SM-S921B) AppleWebKit/537.36 (KHTML, like Gecko) "
    "SamsungBrowser/28.0 Chrome/130.0.0.0 Mobile Safari/537.36"
)
IPAD = (
    "Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"
)
ANDROID_TABLETA = (
    "Mozilla/5.0 (Linux; Android 14; SM-X710) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
)
OPERA = f"{CHROME_WIN} OPR/123.0.0.0"


@pytest.mark.parametrize(
    ("ua", "navegador", "dispositivo"),
    [
        (CHROME_WIN, "Chrome 141", "escritorio"),
        (EDGE, "Edge 141", "escritorio"),
        (OPERA, "Opera 123", "escritorio"),
        (FIREFOX, "Firefox 144", "escritorio"),
        (SAFARI_MAC, "Safari 26", "escritorio"),
        (IPHONE, "Safari 26", "movil"),
        (IPHONE_CHROME, "Chrome 141", "movil"),
        (ANDROID, "Chrome 141", "movil"),
        (SAMSUNG, "Samsung Internet 28", "movil"),
        (IPAD, "Safari 18", "tableta"),
        (ANDROID_TABLETA, "Chrome 141", "tableta"),
        ("curl/8.5.0", "", "escritorio"),
        (None, "", "escritorio"),
    ],
)
def test_navegador_y_dispositivo(ua, navegador, dispositivo) -> None:
    agente = describir(ua)
    assert agente.navegador == navegador
    assert agente.dispositivo == dispositivo


def test_recorta_el_agente_crudo() -> None:
    assert len(describir("x" * 900).crudo) == 300
