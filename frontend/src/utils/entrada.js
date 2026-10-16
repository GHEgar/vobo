const INTENTO = 'vobo:intento-entrada';
const CERRADA = 'vobo:sesion-cerrada';
export const ESPERA_REINTENTO_MS = 30 * 1000;

const leer = (clave) => {
    try {
        return window.sessionStorage.getItem(clave);
    } catch {
        return null;
    }
};

const escribir = (clave, valor) => {
    try {
        if (valor === null) window.sessionStorage.removeItem(clave);
        else window.sessionStorage.setItem(clave, valor);
    } catch {
        return;
    }
};

export const marcarSesionCerrada = () => escribir(CERRADA, '1');

export const limpiarMarcasEntrada = () => {
    escribir(INTENTO, null);
    escribir(CERRADA, null);
};

export const estadoEntrada = (ahora = Date.now()) => {
    if (leer(CERRADA)) return 'cerrada';
    const intento = Number(leer(INTENTO));
    if (intento && ahora - intento >= 0 && ahora - intento < ESPERA_REINTENTO_MS) return 'error';
    return 'redirigiendo';
};

export const irAlLogin = ({ pathname, search }) => {
    limpiarMarcasEntrada();
    escribir(INTENTO, String(Date.now()));
    window.location.assign(`/api/auth/login?siguiente=${encodeURIComponent(`${pathname}${search}`)}`);
};
