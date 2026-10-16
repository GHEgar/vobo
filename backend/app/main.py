from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import (
    accesos,
    actividad,
    admin,
    aprobaciones,
    auth,
    auth_cuentas,
    avisos,
    buscar,
    casos,
    comentarios,
    configuracion,
    contenido,
    cuentas,
    editor,
    editor_contenido,
    evidencias,
    fallas,
    herramientas,
    instancia,
    presencia,
    proyectos,
    rondas,
    secciones,
    tablero,
    version,
)
from app.core.config import settings
from app.inicializar import preparar_base


@asynccontextmanager
async def ciclo_de_vida(_app: FastAPI) -> AsyncIterator[None]:
    preparar_base()
    yield


def create_app() -> FastAPI:
    aplicacion = FastAPI(
        title="VoBo",
        lifespan=ciclo_de_vida,
        docs_url="/api/docs" if settings.app_env == "dev" else None,
        redoc_url=None,
        openapi_url="/api/openapi.json" if settings.app_env == "dev" else None,
    )
    for modulo in (
        auth,
        auth_cuentas,
        admin,
        configuracion,
        editor,
        editor_contenido,
        instancia,
        proyectos,
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
        buscar,
        presencia,
        actividad,
        version,
    ):
        aplicacion.include_router(modulo.router)

    @aplicacion.get("/health")
    def health() -> dict[str, str]:
        return {"estado": "ok"}

    if settings.app_env == "dev":
        media = (
            Path(settings.media_dir)
            if settings.contenido_en_base
            else Path(settings.contenido_dir) / "media"
        )
        aplicacion.mount("/media", StaticFiles(directory=media, check_dir=False), name="media")
    return aplicacion


app = create_app()
