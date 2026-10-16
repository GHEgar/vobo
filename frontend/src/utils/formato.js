const FECHA = new Intl.DateTimeFormat('es-MX', { dateStyle: 'medium', timeStyle: 'short' });
const PORCENTAJE = new Intl.NumberFormat('es-MX', { style: 'percent', maximumFractionDigits: 0 });

const RELATIVA = new Intl.RelativeTimeFormat('es-MX', { numeric: 'auto' });
const UNIDADES = [
    ['minute', 60, 60],
    ['hour', 60 * 60, 24],
    ['day', 24 * 60 * 60, 7],
];

export const aFecha = (valor) => {
    const texto = typeof valor === 'string' && !/[zZ]|[+-]\d\d:\d\d$/.test(valor) ? `${valor}Z` : valor;
    return new Date(texto);
};

export const formatearFecha = (valor) => {
    if (!valor) return '—';
    const fecha = aFecha(valor);
    return Number.isNaN(fecha.getTime()) ? '—' : FECHA.format(fecha);
};

export const formatearRelativa = (valor, ahora = Date.now()) => {
    if (!valor) return '—';
    const fecha = aFecha(valor);
    if (Number.isNaN(fecha.getTime())) return '—';
    const segundos = Math.round((fecha.getTime() - ahora) / 1000);
    if (Math.abs(segundos) < 60) return 'hace un momento';
    const unidad = UNIDADES.find(([, tamano, tope]) => Math.abs(segundos) < tamano * tope);
    return unidad ? RELATIVA.format(Math.round(segundos / unidad[1]), unidad[0]) : FECHA.format(fecha);
};

export const formatearPorcentaje = (parte, total) => PORCENTAJE.format(total ? parte / total : 0);

const NAVEGADORES = [
    [/Edg\/(\d+)/, 'Edge'],
    [/OPR\/(\d+)/, 'Opera'],
    [/Firefox\/(\d+)/, 'Firefox'],
    [/Chrome\/(\d+)/, 'Chrome'],
    [/Version\/(\d+).*Safari/, 'Safari'],
];

const SISTEMAS = [
    [/Windows/, 'Windows'],
    [/Android/, 'Android'],
    [/iPhone|iPad/, 'iOS'],
    [/Mac OS X/, 'macOS'],
    [/Linux/, 'Linux'],
];

export const describirNavegador = (ua = navigator.userAgent) => {
    const navegador = NAVEGADORES.find(([patron]) => patron.test(ua));
    const sistema = SISTEMAS.find(([patron]) => patron.test(ua));
    const nombre = navegador ? `${navegador[1]} ${ua.match(navegador[0])[1]}` : 'Navegador desconocido';
    return sistema ? `${nombre} en ${sistema[1]}` : nombre;
};

export const iniciales = (nombre = '') => nombre
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0].toUpperCase())
    .join('') || '?';
