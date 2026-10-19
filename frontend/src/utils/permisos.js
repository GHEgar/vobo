export const PERMISOS = {
    ejecutarCasos: 'validacion.casos.ejecutar',
    verTablero: 'validacion.tablero.ver',
    verParticipacion: 'validacion.participacion.ver',
    verFallas: 'validacion.fallas.ver',
    gestionarFallas: 'validacion.fallas.gestionar',
    gestionarRondas: 'validacion.rondas.gestionar',
    gestionarAccesos: 'validacion.accesos.gestionar',
    aprobar: 'validacion.herramientas.aprobar',
    administrar: 'validacion.admin',
    editarContenido: 'validacion.contenido.editar',
    gestionarPersonas: 'validacion.personas.gestionar',
    gestionarRoles: 'validacion.roles.gestionar',
    gestionarProyectos: 'validacion.proyectos.gestionar',
    editarIdentidad: 'validacion.identidad.editar',
    editarConfiguracion: 'validacion.configuracion.editar',
};

export const puedeSeguir = (puede) => puede(PERMISOS.verTablero) || puede(PERMISOS.gestionarFallas);
