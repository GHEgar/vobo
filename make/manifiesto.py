from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

MANIFIESTO = "manifiesto.json"
BASE = "base.sqlite3"


def sha256(ruta: Path) -> str:
    resumen = hashlib.sha256()
    with ruta.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(1 << 20), b""):
            resumen.update(bloque)
    return resumen.hexdigest()


def conteos(base: Path) -> dict[str, int]:
    conexion = sqlite3.connect(f"file:{base}?mode=ro", uri=True)
    try:
        tablas = [
            fila[0]
            for fila in conexion.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' "
                "AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]
        return {
            tabla: conexion.execute(f'SELECT COUNT(*) FROM "{tabla}"').fetchone()[0]
            for tabla in tablas
        }
    finally:
        conexion.close()


def revision(base: Path) -> str:
    conexion = sqlite3.connect(f"file:{base}?mode=ro", uri=True)
    try:
        fila = conexion.execute("SELECT version_num FROM alembic_version").fetchone()
    except sqlite3.Error:
        return ""
    finally:
        conexion.close()
    return fila[0] if fila else ""


def leer(carpeta: Path) -> dict:
    return json.loads((carpeta / MANIFIESTO).read_text(encoding="utf-8"))


def crear(carpeta: Path, proyecto: str, version: str, commit: str) -> int:
    archivos = {
        ruta.name: {"sha256": sha256(ruta), "bytes": ruta.stat().st_size}
        for ruta in sorted(carpeta.iterdir())
        if ruta.is_file() and ruta.name != MANIFIESTO
    }
    manifiesto = {
        "formato": 1,
        "creado": datetime.now().astimezone().isoformat(timespec="seconds"),
        "proyecto": proyecto,
        "app_version": version,
        "git": commit,
        "alembic": revision(carpeta / BASE),
        "tablas": conteos(carpeta / BASE),
        "archivos": archivos,
    }
    destino = carpeta / MANIFIESTO
    destino.write_text(json.dumps(manifiesto, indent=2, ensure_ascii=False) + "\n", "utf-8")
    destino.chmod(0o600)
    return 0


def verificar(carpeta: Path) -> int:
    errores = []
    for nombre, datos in leer(carpeta)["archivos"].items():
        ruta = carpeta / nombre
        if not ruta.is_file():
            errores.append(f"falta {nombre}")
        elif sha256(ruta) != datos["sha256"]:
            errores.append(f"sha256 distinto en {nombre}")
    for error in errores:
        print(error)
    return 1 if errores else 0


def campo(carpeta: Path, nombre: str) -> int:
    print(leer(carpeta).get(nombre, ""))
    return 0


def comparar(carpeta: Path, base: Path) -> int:
    esperados = leer(carpeta)["tablas"]
    actuales = conteos(base)
    for tabla in sorted(set(esperados) | set(actuales)):
        esperado = esperados.get(tabla, "-")
        actual = actuales.get(tabla, "-")
        marca = "igual" if esperado == actual else "distinto"
        print(f"{tabla}\t{esperado}\t{actual}\t{marca}")
    return 0


def main() -> int:
    lector = argparse.ArgumentParser(prog="manifiesto.py")
    ordenes = lector.add_subparsers(dest="orden", required=True)
    nuevo = ordenes.add_parser("crear")
    nuevo.add_argument("carpeta", type=Path)
    nuevo.add_argument("--proyecto", default="")
    nuevo.add_argument("--version", default="")
    nuevo.add_argument("--git", default="")
    ordenes.add_parser("verificar").add_argument("carpeta", type=Path)
    leido = ordenes.add_parser("campo")
    leido.add_argument("carpeta", type=Path)
    leido.add_argument("nombre")
    cotejo = ordenes.add_parser("comparar")
    cotejo.add_argument("carpeta", type=Path)
    cotejo.add_argument("base", type=Path)
    args = lector.parse_args()
    if args.orden == "crear":
        return crear(args.carpeta, args.proyecto, args.version, args.git)
    if args.orden == "verificar":
        return verificar(args.carpeta)
    if args.orden == "campo":
        return campo(args.carpeta, args.nombre)
    return comparar(args.carpeta, args.base)


if __name__ == "__main__":
    sys.exit(main())
