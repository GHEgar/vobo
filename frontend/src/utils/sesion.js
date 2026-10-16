export const CLAVE_SESION = ['sesion'];

const PROPIAS = new Set(['/auth/me', '/auth/entrar']);

export const vencioLaSesion = (estado, ruta, sesion) => estado === 401 && !PROPIAS.has(ruta.split('?')[0]) && Boolean(sesion);
