import httpx

TIEMPO_LIMITE = 10.0

transporte: httpx.AsyncBaseTransport | None = None


def cliente_http() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=TIEMPO_LIMITE, transport=transporte)
