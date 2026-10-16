import sys
from pathlib import Path


def limpiar(ruta: Path) -> None:
    lineas = ruta.read_text(encoding="utf-8").splitlines(keepends=True)
    ruta.write_text(
        "".join(linea for linea in lineas if not linea.strip().startswith("# ###")),
        encoding="utf-8",
    )


if __name__ == "__main__":
    for argumento in sys.argv[1:]:
        limpiar(Path(argumento))
