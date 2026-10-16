let csrfToken = '';
let alNoAutenticado = () => {};

export const fijarAlNoAutenticado = (funcion) => {
    alNoAutenticado = funcion;
};

export const fijarCsrf = (token) => {
    csrfToken = token || '';
};

export class ErrorApi extends Error {
    constructor(mensaje, estado, detalle = null) {
        super(mensaje);
        this.estado = estado;
        this.detalle = detalle;
    }
}

const leerDetalle = async (respuesta) => {
    try {
        const cuerpo = await respuesta.json();
        if (typeof cuerpo.detail === 'string') return { mensaje: cuerpo.detail };
        if (Array.isArray(cuerpo.detail)) return { mensaje: 'Revisa los datos del formulario', detalle: cuerpo.detail };
    } catch {
        return { mensaje: `Error ${respuesta.status}` };
    }
    return { mensaje: `Error ${respuesta.status}` };
};

export const solicitar = async (ruta, { method = 'GET', json, form, signal, espera } = {}) => {
    const headers = { Accept: 'application/json' };
    if (method !== 'GET') headers['X-CSRF-Token'] = csrfToken;
    if (json !== undefined) headers['Content-Type'] = 'application/json';
    let respuesta;
    try {
        respuesta = await fetch(`/api${ruta}`, {
            method,
            headers,
            credentials: 'same-origin',
            body: json !== undefined ? JSON.stringify(json) : form,
            signal: signal ?? AbortSignal.timeout(espera ?? (form ? 60000 : 10000)),
        });
    } catch {
        throw new ErrorApi('No se pudo conectar con el servidor', 0);
    }
    if (!respuesta.ok) {
        const { mensaje, detalle } = await leerDetalle(respuesta);
        if (respuesta.status === 401) alNoAutenticado(ruta);
        throw new ErrorApi(mensaje, respuesta.status, detalle);
    }
    if (respuesta.status === 204) return null;
    return respuesta.json();
};

export const consulta = (params) => {
    const limpios = Object.entries(params).filter(([, valor]) => valor !== '' && valor != null);
    return limpios.length ? `?${new URLSearchParams(limpios)}` : '';
};
