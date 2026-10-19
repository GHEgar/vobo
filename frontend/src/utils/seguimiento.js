import { aFecha } from '@/utils/formato';

const DIA = new Intl.DateTimeFormat('es-MX', { dateStyle: 'medium' });
const MINUTO = 60 * 1000;
const HORA = 60 * MINUTO;
const JORNADA = 24 * HORA;

const dosDigitos = (n) => String(n).padStart(2, '0');

export const hoyISO = (ahora = new Date()) => `${ahora.getFullYear()}-${dosDigitos(ahora.getMonth() + 1)}-${dosDigitos(ahora.getDate())}`;

export const formatearDia = (iso) => {
    if (!iso) return '—';
    const [anio, mes, dia] = iso.split('-').map(Number);
    return DIA.format(new Date(anio, mes - 1, dia));
};

export const milisegundos = (desde, hasta) => {
    if (!desde || !hasta) return null;
    const total = aFecha(hasta).getTime() - aFecha(desde).getTime();
    return Number.isNaN(total) ? null : Math.max(total, 0);
};

export const formatearDuracion = (total) => {
    if (total === null || total === undefined) return '';
    if (total < HORA) return `${Math.max(Math.round(total / MINUTO), 1)} min`;
    if (total < JORNADA) return `${Math.round(total / HORA)} h`;
    const dias = Math.floor(total / JORNADA);
    const horas = Math.round((total - dias * JORNADA) / HORA);
    return horas ? `${dias} d ${horas} h` : `${dias} d`;
};

export const duracion = (desde, hasta) => formatearDuracion(milisegundos(desde, hasta));

export const vencido = (plazo, resuelto, hoy = hoyISO()) => Boolean(plazo) && !resuelto && plazo < hoy;

const nombreEstado = (estados, valor) => estados[valor]?.texto ?? valor;

export const describirEvento = (evento, estados) => {
    const quien = evento.autor || evento.autor_email;
    if (evento.accion === 'estado') {
        return `${quien} cambió el estado de ${nombreEstado(estados, evento.anterior)} a ${nombreEstado(estados, evento.nuevo)}`;
    }
    if (evento.accion === 'plazo') {
        if (!evento.nuevo) return `${quien} quitó el plazo`;
        if (!evento.anterior) return `${quien} fijó el plazo al ${formatearDia(evento.nuevo)}`;
        return `${quien} movió el plazo del ${formatearDia(evento.anterior)} al ${formatearDia(evento.nuevo)}`;
    }
    if (evento.accion === 'nota') {
        return evento.texto ? `${quien} actualizó la nota de resolución: «${evento.texto}»` : `${quien} borró la nota de resolución`;
    }
    return quien;
};
