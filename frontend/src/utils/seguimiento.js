import { aFecha } from '@/utils/formato';

const DIA = new Intl.DateTimeFormat('es-MX', { dateStyle: 'medium' });
const MINUTO = 60 * 1000;
const HORA = 60 * MINUTO;
const JORNADA = 24 * HORA;

const HORAS_DIA = 8;
const RESUELTOS = new Set(['cerrada', 'resuelto']);

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

export const AYUDA_ESFUERZO = `${HORAS_DIA} h = 1 día`;

const decimal = (n) => String(Number(n.toFixed(1)));

export const formatearEsfuerzo = (horas) => {
    if (horas === null || horas === undefined || horas === '') return '';
    const valor = Number(horas);
    if (Number.isNaN(valor)) return '';
    return valor < HORAS_DIA ? `${decimal(valor)} h` : `${decimal(valor / HORAS_DIA)} d`;
};

export const resuelto = (registro) => RESUELTOS.has(registro.estado);

export const sumarEsfuerzo = (registros) => registros.reduce((suma, r) => {
    if (r.principal || r.esfuerzo_horas === null || r.esfuerzo_horas === undefined) {
        return { ...suma, sinEstimar: suma.sinEstimar + (r.principal ? 0 : 1) };
    }
    return {
        ...suma,
        total: suma.total + r.esfuerzo_horas,
        pendiente: suma.pendiente + (resuelto(r) ? 0 : r.esfuerzo_horas),
    };
}, { total: 0, pendiente: 0, sinEstimar: 0 });

export const idRegistro = (objeto, id) => `registro-${objeto}-${id}`;

export const etiquetaFalla = (f) => `#${f.id} · ${f.caso_id}`;
export const etiquetaComentario = (c) => `${c.caso_id} · ${c.tipo === 'no_pude' ? 'no pude' : `paso ${c.paso + 1}`}`;

const nombreEstado = (estados, valor) => estados[valor]?.texto ?? valor;

const via = (evento) => (evento.texto ? `, con ${evento.texto}` : '');

const describirEsfuerzo = (quien, { anterior, nuevo }) => {
    if (!nuevo) return `${quien} quitó la estimación de esfuerzo`;
    if (!anterior) return `${quien} estimó el esfuerzo en ${formatearEsfuerzo(nuevo)}`;
    return `${quien} cambió el esfuerzo de ${formatearEsfuerzo(anterior)} a ${formatearEsfuerzo(nuevo)}`;
};

export const describirEvento = (evento, estados) => {
    const quien = evento.autor || evento.autor_email;
    if (evento.accion === 'estado') {
        return `${quien} cambió el estado de ${nombreEstado(estados, evento.anterior)} a ${nombreEstado(estados, evento.nuevo)}${via(evento)}`;
    }
    if (evento.accion === 'plazo') {
        if (!evento.nuevo) return `${quien} quitó el plazo${via(evento)}`;
        if (!evento.anterior) return `${quien} fijó el plazo al ${formatearDia(evento.nuevo)}${via(evento)}`;
        return `${quien} movió el plazo del ${formatearDia(evento.anterior)} al ${formatearDia(evento.nuevo)}${via(evento)}`;
    }
    if (evento.accion === 'esfuerzo') return describirEsfuerzo(quien, evento);
    if (evento.accion === 'vinculo') {
        return evento.nuevo ? `${quien} indicó que se resuelve con ${evento.texto}` : `${quien} quitó el vínculo con ${evento.texto}`;
    }
    if (evento.accion === 'nota') {
        return evento.texto ? `${quien} actualizó la nota de resolución: «${evento.texto}»` : `${quien} borró la nota de resolución`;
    }
    return quien;
};
