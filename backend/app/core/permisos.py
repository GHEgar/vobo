EJECUTAR_CASOS = "validacion.casos.ejecutar"
VER_TABLERO = "validacion.tablero.ver"
GESTIONAR_FALLAS = "validacion.fallas.gestionar"
APROBAR = "validacion.herramientas.aprobar"
ADMINISTRAR = "validacion.admin"
EDITAR_CONTENIDO = "validacion.contenido.editar"

TODOS = frozenset({EJECUTAR_CASOS, VER_TABLERO, GESTIONAR_FALLAS})

CATALOGO = {
    EJECUTAR_CASOS: "Ejecutar los casos asignados y reportar fallas",
    VER_TABLERO: "Ver el tablero de avance de la ronda",
    GESTIONAR_FALLAS: "Gestionar fallas, rondas, asignaciones y accesos",
    APROBAR: "Aprobar o rechazar herramientas y características",
    EDITAR_CONTENIDO: "Editar secciones, casos, procedimientos y animaciones del contenido",
}

TODOS_CON_ADMIN = frozenset(CATALOGO) | {ADMINISTRAR}


def expandir(permisos: set[str] | frozenset[str]) -> frozenset[str]:
    if ADMINISTRAR in permisos:
        return frozenset(permisos) | TODOS_CON_ADMIN
    return frozenset(permisos)
