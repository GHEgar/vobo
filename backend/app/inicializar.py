import sys
from pathlib import Path

from sqlalchemy import Engine
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.core.config import settings
from app.core.database import engine
from app.core.migraciones import EsquemaIncompatible, migrar
from app.services import proyectos
from app.services.contenido_importacion import importar_inicial


def preparar_base(motor: Engine | None = None) -> None:
    migrar(motor or engine)
    Path(settings.evidencias_dir).mkdir(parents=True, exist_ok=True)
    with Session(motor or engine) as db:
        proyectos.asegurar_por_omision(db)
    if settings.contenido_en_base:
        importar_inicial(motor or engine)


if __name__ == "__main__":
    try:
        preparar_base()
    except EsquemaIncompatible as error:
        print(f"inicializar: {error}", file=sys.stderr)
        sys.exit(1)
