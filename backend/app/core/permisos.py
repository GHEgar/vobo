EJECUTAR_CASOS = "validacion.casos.ejecutar"
VER_TABLERO = "validacion.tablero.ver"
VER_PARTICIPACION = "validacion.participacion.ver"
VER_FALLAS = "validacion.fallas.ver"
GESTIONAR_FALLAS = "validacion.fallas.gestionar"
GESTIONAR_RONDAS = "validacion.rondas.gestionar"
GESTIONAR_ACCESOS = "validacion.accesos.gestionar"
APROBAR = "validacion.herramientas.aprobar"
EDITAR_CONTENIDO = "validacion.contenido.editar"
GESTIONAR_PERSONAS = "validacion.personas.gestionar"
GESTIONAR_ROLES = "validacion.roles.gestionar"
GESTIONAR_PROYECTOS = "validacion.proyectos.gestionar"
EDITAR_IDENTIDAD = "validacion.identidad.editar"
EDITAR_CONFIGURACION = "validacion.configuracion.editar"
ADMINISTRAR = "validacion.admin"

TODOS = frozenset({EJECUTAR_CASOS, VER_TABLERO, GESTIONAR_FALLAS})

AREAS: dict[str, dict[str, str]] = {
    "Validación": {
        EJECUTAR_CASOS: "Ejecutar los casos asignados y reportar fallas",
        VER_TABLERO: "Ver el tablero de avance de la ronda",
        VER_PARTICIPACION: "Ver la página Participación",
        VER_FALLAS: "Ver fallas, comentarios y el informe, sin cambiarlos",
        GESTIONAR_FALLAS: "Gestionar fallas y comentarios; incluye ver fallas, rondas y accesos",
        GESTIONAR_RONDAS: "Crear, cerrar y borrar rondas y asignar secciones",
        GESTIONAR_ACCESOS: "Otorgar páginas a personas",
        APROBAR: "Aprobar o rechazar herramientas y características",
    },
    "Contenido": {
        EDITAR_CONTENIDO: "Editar secciones, casos, procedimientos y animaciones del contenido",
    },
    "Administración": {
        GESTIONAR_PERSONAS: "Invitar personas y gestionar sus cuentas",
        GESTIONAR_ROLES: "Crear y editar roles y asignarlos a personas",
        GESTIONAR_PROYECTOS: "Crear, ordenar, editar y archivar proyectos",
        EDITAR_IDENTIDAD: "Editar nombre, textos de entrada, marca, colores y tipografía",
        EDITAR_CONFIGURACION: "Editar sistemas y cuentas de prueba de la instancia",
    },
}

CATALOGO = {
    permiso: descripcion for area in AREAS.values() for permiso, descripcion in area.items()
}
AREA_DE = {permiso: nombre for nombre, area in AREAS.items() for permiso in area}

ADMINISTRACION = frozenset(AREAS["Administración"])

IMPLICA: dict[str, frozenset[str]] = {
    GESTIONAR_FALLAS: frozenset(
        {VER_FALLAS, GESTIONAR_RONDAS, GESTIONAR_ACCESOS, VER_PARTICIPACION}
    ),
    VER_TABLERO: frozenset({VER_PARTICIPACION}),
}

TODOS_CON_ADMIN = frozenset(CATALOGO) | {ADMINISTRAR}


def expandir(permisos: set[str] | frozenset[str]) -> frozenset[str]:
    if ADMINISTRAR in permisos:
        return frozenset(permisos) | TODOS_CON_ADMIN
    salida = set(permisos)
    pendientes = list(salida)
    while pendientes:
        for implicado in IMPLICA.get(pendientes.pop(), frozenset()):
            if implicado not in salida:
                salida.add(implicado)
                pendientes.append(implicado)
    return frozenset(salida)
