from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import (
    accesos,
    aprobaciones,
    auth,
    avisos,
    casos,
    comentarios,
    contenido,
    cuentas,
    evidencias,
    fallas,
    herramientas,
    instancia,
    rondas,
    secciones,
    tablero,
)
from app.core.config import settings
from app.inicializar import preparar_base


@asynccontextmanager
async def ciclo_de_vida(_app: FastAPI) -> AsyncIterator[None]:
    preparar_base()
    yield


def create_app() -> FastAPI:
    aplicacion = FastAPI(
        title="Validaciones",
        lifespan=ciclo_de_vida,
        docs_url="/api/docs" if settings.app_env == "dev" else None,
        redoc_url=None,
        openapi_url="/api/openapi.json" if settings.app_env == "dev" else None,
    )
    for modulo in (
        auth,
        instancia,
        contenido,
        rondas,
        casos,
        fallas,
        evidencias,
        tablero,
        herramientas,
        comentarios,
        accesos,
        aprobaciones,
        secciones,
        cuentas,
        avisos,
    ):
        aplicacion.include_router(modulo.router)

    @aplicacion.get("/health")
    def health() -> dict[str, str]:
        return {"estado": "ok"}

    if settings.app_env == "dev":
        media = Path(settings.contenido_dir) / "media"
        aplicacion.mount("/media", StaticFiles(directory=media, check_dir=False), name="media")
    return aplicacion


app = create_app()
