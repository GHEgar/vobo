import { PERMISOS } from '@/utils/permisos';

export const rolesDe = (permisos = []) => {
    if (permisos.includes(PERMISOS.gestionarFallas)) return ['coordinación'];
    if (permisos.includes(PERMISOS.ejecutarCasos)) return ['validador'];
    return [];
};

export const PAGINAS_OTORGABLES = [
    { pagina: 'tablero', texto: 'Tablero', permiso: PERMISOS.verTablero },
    { pagina: 'fallas', texto: 'Fallas', permiso: PERMISOS.gestionarFallas },
    { pagina: 'herramientas', texto: 'Herramientas', permiso: PERMISOS.gestionarFallas },
    { pagina: 'tecnico', texto: 'Técnico', permiso: PERMISOS.gestionarFallas },
];
