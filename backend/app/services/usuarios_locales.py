from dataclasses import dataclass

from app.core.permisos import APROBAR, EJECUTAR_CASOS, TODOS


@dataclass(frozen=True)
class UsuarioDePrueba:
    clave: str
    nombre: str
    email: str
    rol: str
    permisos: frozenset[str]


USUARIOS_LOCALES = (
    UsuarioDePrueba(
        "validador",
        "Valeria Validadora",
        "validador@local.test",
        "Validación - validador",
        frozenset({EJECUTAR_CASOS}),
    ),
    UsuarioDePrueba(
        "coordinacion",
        "Carlos Coordinación",
        "coordinacion@local.test",
        "Validación - coordinación",
        TODOS,
    ),
    UsuarioDePrueba(
        "aprobacion",
        "Ana Aprobadora",
        "aprobacion@local.test",
        "Validación - aprobación",
        frozenset({APROBAR}),
    ),
    UsuarioDePrueba(
        "sin-rol",
        "Sofía Sin Rol",
        "sinrol@local.test",
        "Sin rol en validación",
        frozenset(),
    ),
)


def por_clave(clave: str) -> UsuarioDePrueba | None:
    return next((u for u in USUARIOS_LOCALES if u.clave == clave), None)
