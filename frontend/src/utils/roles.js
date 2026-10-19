import { PERMISOS } from '@/utils/permisos';

export const rolesDe = (permisos = []) => {
    if (permisos.includes(PERMISOS.administrar)) return ['administración'];
    if (permisos.includes(PERMISOS.gestionarFallas)) return ['coordinación'];
    if (permisos.includes(PERMISOS.ejecutarCasos)) return ['validador'];
    return [];
};

export const PAGINAS_OTORGABLES = [
    { pagina: 'tablero', texto: 'Tablero', permiso: PERMISOS.verTablero },
    { pagina: 'participacion', texto: 'Participación', permiso: PERMISOS.verParticipacion },
    { pagina: 'fallas', texto: 'Fallas', permiso: PERMISOS.verFallas },
    { pagina: 'herramientas', texto: 'Herramientas', permiso: PERMISOS.gestionarFallas },
    { pagina: 'tecnico', texto: 'Técnico', permiso: PERMISOS.gestionarFallas },
];
