export const ANCHO = 1920;
export const ALTO = 1080;

export const PALETA = {
    fondo: '#121417',
    fondoGrafo: '#0E1013',
    halo: '#161A1F',
    tarjeta: '#1A1D21',
    tarjetaAlta: '#22262B',
    pista: '#2A2E33',
    texto: '#F2F3F5',
    medio: '#C9CDD2',
    tenue: '#A7ADB4',
    apagado: '#7E858C',
    enlace: '#5A6168',
    blanco: '#FFFFFF',
    vivo: '#0CA30C',
    fallaTexto: '#FF7B72',
    leyendaPersona: '#6250D6',
};

export const ESTADOS = {
    pasa: '#0CA30C',
    falla: '#D03B3B',
    no_pude: '#FAB219',
    pendiente: '#3A3F45',
};

export const ORDEN_ESTADOS = ['pasa', 'falla', 'no_pude'];

export const NOMBRES_ESTADO = { pasa: 'Pasa', falla: 'Falla', no_pude: 'No pude', pendiente: 'Pendiente' };

export const translucido = (alfa) => `rgba(26, 29, 33, ${alfa})`;
