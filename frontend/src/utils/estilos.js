export const RUTA_ESTILOS = '/api/instancia/tema.css';

export const recargarEstilos = (ahora = Date.now()) => {
    const enlace = document.querySelector(`link[rel="stylesheet"][href^="${RUTA_ESTILOS}"]`);
    if (enlace) enlace.setAttribute('href', `${RUTA_ESTILOS}?v=${ahora}`);
};

export const COLOR_HEX = /^#[0-9A-Fa-f]{6}$/;

export const variablesDeColor = (colores) => Object.fromEntries(
    Object.entries(colores).filter(([, valor]) => COLOR_HEX.test(valor)).map(([token, valor]) => [`--color-${token}`, valor]),
);

export const colorActual = (token) => {
    const valor = getComputedStyle(document.documentElement).getPropertyValue(`--color-${token}`).trim();
    return COLOR_HEX.test(valor) ? valor.toUpperCase() : '#000000';
};

const FAMILIAS = {
    producto: "'Rotulo', system-ui, sans-serif",
    sistema: 'system-ui, sans-serif',
};

export const variablesDeFuente = (fuente) => {
    const familia = FAMILIAS[fuente];
    if (!familia) return {};
    return { '--tipo-negrita': familia, '--tipo-media': familia, '--tipo-regular': familia };
};
