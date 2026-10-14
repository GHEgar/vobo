const FECHA = new Intl.DateTimeFormat('es-MX', { dateStyle: 'medium', timeStyle: 'short' });
const PORCENTAJE = new Intl.NumberFormat('es-MX', { style: 'percent', maximumFractionDigits: 0 });

export const formatearFecha = (valor) => {
    if (!valor) return '—';
    const texto = typeof valor === 'string' && !/[zZ]|[+-]\d\d:\d\d$/.test(valor) ? `${valor}Z` : valor;
    const fecha = new Date(texto);
    return Number.isNaN(fecha.getTime()) ? '—' : FECHA.format(fecha);
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
