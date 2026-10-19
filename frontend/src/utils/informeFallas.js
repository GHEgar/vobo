import { ESTADOS_FALLA, SEVERIDADES } from '@/utils/etiquetas';
import { formatearDuracion, formatearEsfuerzo, milisegundos, sumarEsfuerzo, vencido } from '@/utils/seguimiento';

export const zonaHoraria = () => Intl.DateTimeFormat().resolvedOptions().timeZone;

export const pasoDeFalla = (falla) => (falla.paso === null ? 'Fuera de los pasos' : `${falla.paso + 1}. ${falla.paso_texto}`);

export const PARTES = [
    { valor: 'resumen', texto: 'Resumen' },
    { valor: 'participacion', texto: 'Participación' },
    { valor: 'fallas', texto: 'Fallas' },
    { valor: 'no_pude', texto: '«No pude probarlo»' },
    { valor: 'comentarios', texto: 'Comentarios' },
    { valor: 'seguimiento', texto: 'Respuestas e historial' },
    { valor: 'evidencias', texto: 'Evidencias' },
    { valor: 'tiempos', texto: 'Tiempos y plazos' },
];

export const SITUACIONES = [
    { valor: 'abiertas', texto: 'Abiertas' },
    { valor: 'resueltas', texto: 'Resueltas' },
];

const LEGADOS = ['tipo', 'comentarios', 'sistema'];

const lista = (texto) => (texto ? texto.split(',').filter(Boolean) : []);

const partesDe = (params) => {
    if (params.has('incluir')) return new Set(lista(params.get('incluir')));
    const partes = new Set(PARTES.map((p) => p.valor));
    if (params.get('tipo') === 'falla') partes.delete('no_pude');
    if (params.get('tipo') === 'no_pude') partes.delete('fallas');
    return partes;
};

const proyectosDe = (params, actual, proyectos) => {
    const claves = proyectos.map((p) => p.clave);
    const pedidos = params.has('proyectos')
        ? lista(params.get('proyectos')).filter((c) => claves.includes(c))
        : (params.get('ronda') && actual ? [actual] : []);
    return pedidos.length ? pedidos : proyectos.filter((p) => !p.archivado).map((p) => p.clave);
};

export const opcionesDe = (params, actual, proyectos) => {
    const elegidos = proyectosDe(params, actual, proyectos);
    return {
        proyectos: elegidos,
        ronda: elegidos.length === 1 ? params.get('ronda') ?? '' : '',
        sistemas: params.has('sistemas') ? lista(params.get('sistemas')) : lista(params.get('sistema') ?? ''),
        severidad: params.get('severidad') ?? '',
        estado: params.get('estado') ?? '',
        situacion: params.get('situacion') ?? '',
        incluir: partesDe(params),
    };
};

export const conOpciones = (params, opciones, cambios) => {
    const siguientes = { ...opciones, ...cambios };
    const nuevos = new URLSearchParams(params);
    LEGADOS.forEach((clave) => nuevos.delete(clave));
    const fijar = (clave, valor) => (valor ? nuevos.set(clave, valor) : nuevos.delete(clave));
    fijar('proyectos', siguientes.proyectos.join(','));
    fijar('ronda', 'proyectos' in cambios ? '' : siguientes.ronda);
    fijar('sistemas', siguientes.sistemas.join(','));
    fijar('severidad', siguientes.severidad);
    fijar('estado', 'situacion' in cambios ? '' : siguientes.estado);
    fijar('situacion', siguientes.situacion);
    nuevos.set('incluir', PARTES.map((p) => p.valor).filter((v) => siguientes.incluir.has(v)).join(','));
    return nuevos;
};

const segunSituacion = (situacion, resuelto) => !situacion || (situacion === 'resueltas') === resuelto;

export const fallaResuelta = (f) => f.estado === 'cerrada';
export const comentarioResuelto = (c) => c.estado === 'resuelto';

const ORDEN_SEVERIDAD = Object.keys(SEVERIDADES);

export const filtrarFallas = (fallas, o) => fallas
    .filter((f) => o.incluir.has(f.tipo === 'no_pude' ? 'no_pude' : 'fallas'))
    .filter((f) => !o.sistemas.length || o.sistemas.includes(f.sistema))
    .filter((f) => !o.severidad || f.severidad === o.severidad)
    .filter((f) => !o.estado || f.estado === o.estado)
    .filter((f) => segunSituacion(o.situacion, fallaResuelta(f)))
    .sort((a, b) => ORDEN_SEVERIDAD.indexOf(a.severidad) - ORDEN_SEVERIDAD.indexOf(b.severidad) || a.creada.localeCompare(b.creada));

export const filtrarComentarios = (comentarios, o) => (o.incluir.has('comentarios') ? comentarios : [])
    .filter((c) => !o.sistemas.length || o.sistemas.includes(c.sistema))
    .filter((c) => segunSituacion(o.situacion, comentarioResuelto(c)))
    .sort((a, b) => a.actualizado.localeCompare(b.actualizado));

export const agruparPorHerramienta = (fallas, comentarios, nombre) => {
    const grupos = new Map();
    const grupo = (clave) => {
        if (!grupos.has(clave)) grupos.set(clave, { clave, nombre: clave ? nombre(clave) : 'Sin herramienta', fallas: [], comentarios: [] });
        return grupos.get(clave);
    };
    fallas.forEach((f) => grupo(f.sistema).fallas.push(f));
    comentarios.forEach((c) => grupo(c.sistema).comentarios.push(c));
    return [...grupos.values()].sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'));
};

export const herramientasDe = (porProyecto) => [...new Set(porProyecto.flatMap((p) => [
    ...p.fallas.map((f) => f.sistema),
    ...p.comentarios.map((c) => c.sistema),
]))].filter(Boolean).sort((a, b) => a.localeCompare(b, 'es'));

const promedio = (valores) => (valores.length ? valores.reduce((a, b) => a + b, 0) / valores.length : null);

export const resumenProyecto = (fallas, comentarios) => {
    const resueltas = fallas.filter(fallaResuelta);
    const tiempos = resueltas.map((f) => milisegundos(f.creada, f.resuelta_en)).filter((t) => t !== null);
    const comentariosResueltos = comentarios.filter(comentarioResuelto);
    const esfuerzo = sumarEsfuerzo([...fallas, ...comentarios]);
    return {
        fallasAbiertas: fallas.length - resueltas.length,
        fallasResueltas: resueltas.length,
        fallasVencidas: fallas.filter((f) => vencido(f.plazo, fallaResuelta(f))).length,
        tiempoMedio: formatearDuracion(promedio(tiempos)),
        comentariosAbiertos: comentarios.length - comentariosResueltos.length,
        comentariosResueltos: comentariosResueltos.length,
        comentariosVencidos: comentarios.filter((c) => vencido(c.plazo, comentarioResuelto(c))).length,
        esfuerzoTotal: formatearEsfuerzo(esfuerzo.total) || '0 h',
        esfuerzoPendiente: formatearEsfuerzo(esfuerzo.pendiente) || '0 h',
    };
};

export const subtotalEsfuerzo = (registros) => {
    const { total, pendiente } = sumarEsfuerzo(registros);
    if (!total) return '';
    return `Esfuerzo ${formatearEsfuerzo(total)}${pendiente ? `, pendiente ${formatearEsfuerzo(pendiente)}` : ''}`;
};

export const describirOpciones = (o, nombreSistema) => [
    ['Herramientas', o.sistemas.length ? o.sistemas.map(nombreSistema).join(', ') : 'Todas'],
    ['Severidad', SEVERIDADES[o.severidad]?.texto ?? 'Todas'],
    ['Estado', ESTADOS_FALLA[o.estado]?.texto ?? SITUACIONES.find((s) => s.valor === o.situacion)?.texto ?? 'Todas'],
    ['Incluye', PARTES.filter((p) => o.incluir.has(p.valor)).map((p) => p.texto).join(', ') || 'Nada'],
];
