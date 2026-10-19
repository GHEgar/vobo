import { PERMISOS } from '@/utils/permisos';

const MENU = ['tablero', 'participacion', 'fallas', 'herramientas', 'aprobaciones'];

export const paginaUnica = (puede, ve) => {
    if (puede(PERMISOS.ejecutarCasos)) return null;
    const visibles = MENU.filter((p) => ve(p));
    return visibles.length === 1 ? `/${visibles[0]}` : null;
};
