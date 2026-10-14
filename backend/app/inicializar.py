from pathlib import Path

import app.models  # noqa: F401
from app.core.config import settings
from app.core.database import (
    Base,
    asegurar_columnas,
    asegurar_valores,
    engine,
    renombrar_sub,
)


def preparar_base() -> None:
    renombrar_sub()
    Base.metadata.create_all(bind=engine)
    asegurar_columnas()
    asegurar_valores()
    Path(settings.evidencias_dir).mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    preparar_base()
