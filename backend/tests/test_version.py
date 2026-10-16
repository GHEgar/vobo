from app.core.config import settings


def test_version_publica_sin_cache(cliente_de, monkeypatch) -> None:
    monkeypatch.setattr(settings, "app_version", "abc1234-20261015")
    respuesta = cliente_de(None).get("/api/version")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"version": "abc1234-20261015"}
    assert respuesta.headers["cache-control"] == "no-store"


def test_sin_variable_la_version_va_vacia(cliente_de, monkeypatch) -> None:
    monkeypatch.setattr(settings, "app_version", "")
    assert cliente_de(None).get("/api/version").json() == {"version": ""}
