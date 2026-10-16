import { Alert, Bell, Chat, CheckCircle, CloseCircle, Edit, Login, Phone, Play, Send, Table, ThumbDown, ThumbUp } from 'tesela/react';
import { aFecha } from '@/utils/formato';

export const TIPOS = [
    { valor: 'resultado', texto: 'Resultados' },
    { valor: 'falla', texto: 'Fallas' },
    { valor: 'comentario', texto: 'Comentarios' },
    { valor: 'aprobacion', texto: 'Aprobaciones' },
    { valor: 'decision', texto: 'Decisiones' },
    { valor: 'aviso', texto: 'Avisos' },
    { valor: 'sesion', texto: 'Sesiones' },
    { valor: 'contenido', texto: 'Contenido' },
];

export const TONOS_ICONO = {
    exito: 'bg-pasa-fondo text-pasa',
    error: 'bg-falla-fondo text-falla',
    aviso: 'bg-pendiente-fondo text-pendiente',
    marca: 'bg-primario-claro text-primario',
    neutro: 'bg-fondo-suave text-texto-tenue',
};

const RESULTADOS = {
    pasa: { icono: CheckCircle, tono: 'exito' },
    falla: { icono: CloseCircle, tono: 'error' },
    no_pude: { icono: Alert, tono: 'aviso' },
};

const FIJOS = {
    falla: { icono: Alert, tono: 'error' },
    comentario: { icono: Chat, tono: 'marca' },
    decision: { icono: Send, tono: 'marca' },
    aviso: { icono: Bell, tono: 'aviso' },
    sesion: { icono: Login, tono: 'neutro' },
    contenido: { icono: Edit, tono: 'neutro' },
};

export const iconoDeEvento = (evento) => {
    if (evento.tipo === 'resultado') return RESULTADOS[evento.estado] ?? { icono: Play, tono: 'neutro' };
    if (evento.tipo === 'aprobacion') {
        if (evento.estado === 'rechazada') return { icono: ThumbDown, tono: 'error' };
        return { icono: ThumbUp, tono: evento.estado === 'aprobada' ? 'exito' : 'neutro' };
    }
    return FIJOS[evento.tipo] ?? { icono: Edit, tono: 'neutro' };
};

export const DISPOSITIVOS = {
    escritorio: { texto: 'Escritorio', icono: Table },
    tableta: { texto: 'Tableta', icono: Phone },
    movil: { texto: 'Móvil', icono: Phone },
};

export const duracion = (segundos) => {
    const minutos = Math.floor(segundos / 60);
    if (minutos < 1) return 'menos de 1 min';
    if (minutos < 60) return `${minutos} min`;
    const horas = Math.floor(minutos / 60);
    const resto = minutos % 60;
    return resto ? `${horas} h ${resto} min` : `${horas} h`;
};

export const pantallaLegible = (pantalla) => (pantalla ? pantalla.replace('x', '×') : '');

const DIA = new Intl.DateTimeFormat('es-MX', { weekday: 'long', day: 'numeric', month: 'long' });
const HORA = new Intl.DateTimeFormat('es-MX', { hour: '2-digit', minute: '2-digit' });

const claveDia = (fecha) => `${fecha.getFullYear()}-${fecha.getMonth()}-${fecha.getDate()}`;

export const nombreDia = (fecha, ahora = new Date()) => {
    if (claveDia(fecha) === claveDia(ahora)) return 'Hoy';
    const ayer = new Date(ahora);
    ayer.setDate(ayer.getDate() - 1);
    if (claveDia(fecha) === claveDia(ayer)) return 'Ayer';
    const texto = DIA.format(fecha);
    return texto.charAt(0).toUpperCase() + texto.slice(1);
};

export const horaDe = (valor) => HORA.format(aFecha(valor));

export const agruparPorDia = (eventos, ahora = new Date()) => {
    const grupos = [];
    for (const evento of eventos) {
        const fecha = aFecha(evento.cuando);
        const clave = claveDia(fecha);
        const ultimo = grupos.at(-1);
        if (ultimo?.clave === clave) ultimo.eventos.push(evento);
        else grupos.push({ clave, titulo: nombreDia(fecha, ahora), eventos: [evento] });
    }
    return grupos;
};

export const personasDe = (eventos) => {
    const vistas = new Map();
    for (const e of eventos) if (!vistas.has(e.usuario.email)) vistas.set(e.usuario.email, e.usuario.nombre);
    return [...vistas].map(([email, nombre]) => ({ email, nombre })).sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'));
};
