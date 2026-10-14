let csrfToken = '';

export const fijarCsrf = (token) => {
    csrfToken = token || '';
};

export class ErrorApi extends Error {
    constructor(mensaje, estado) {
        super(mensaje);
        this.estado = estado;
    }
}

const leerDetalle = async (respuesta) => {
    try {
        const cuerpo = await respuesta.json();
        if (typeof cuerpo.detail === 'string') return cuerpo.detail;
        if (Array.isArray(cuerpo.detail)) return 'Revisa los datos del formulario';
    } catch {
        return `Error ${respuesta.status}`;
    }
    return `Error ${respuesta.status}`;
};

export const solicitar = async (ruta, { method = 'GET', json, form, signal } = {}) => {
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
            signal: signal ?? AbortSignal.timeout(form ? 60000 : 10000),
        });
    } catch {
        throw new ErrorApi('No se pudo conectar con el servidor', 0);
    }
    if (!respuesta.ok) throw new ErrorApi(await leerDetalle(respuesta), respuesta.status);
    if (respuesta.status === 204) return null;
    return respuesta.json();
};

export const consulta = (params) => {
    const limpios = Object.entries(params).filter(([, valor]) => valor !== '' && valor != null);
    return limpios.length ? `?${new URLSearchParams(limpios)}` : '';
};
