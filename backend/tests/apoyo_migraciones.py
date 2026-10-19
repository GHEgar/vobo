from sqlalchemy import Engine, inspect, text


def volcado(motor: Engine) -> dict[str, list[dict]]:
    with motor.connect() as conexion:
        tablas = [t for t in inspect(conexion).get_table_names() if t != "alembic_version"]
        return {
            t: [
                dict(f)
                for f in conexion.execute(text(f'SELECT * FROM "{t}" ORDER BY 1')).mappings()
            ]
            for t in tablas
        }


def conserva(
    antes: dict[str, list[dict]],
    despues: dict[str, list[dict]],
    crecen: frozenset[str] = frozenset(),
) -> bool:
    def cuadra(tabla: str, filas: list[dict]) -> bool:
        nuevas = despues[tabla]
        return len(nuevas) >= len(filas) if tabla in crecen else len(nuevas) == len(filas)

    return all(
        cuadra(tabla, filas)
        and all(
            all(nueva.get(columna) == valor for columna, valor in vieja.items())
            for vieja, nueva in zip(filas, despues[tabla][: len(filas)], strict=True)
        )
        for tabla, filas in antes.items()
    )
