import { ESTADOS_COMENTARIO, ESTADOS_FALLA, REPRODUCIBLE, SEVERIDADES } from '@/utils/etiquetas';
import { pasoDeFalla } from '@/utils/informeFallas';
import { duracion } from '@/utils/seguimiento';

const BOM = '﻿';
const PELIGROSOS = ['=', '+', '-', '@', '\t', '\r'];

const COLUMNAS = [
    'proyecto', 'herramienta', 'tipo', 'id', 'ronda', 'caso', 'título del caso', 'sección', 'paso',
    'severidad', 'reproducible', 'estado', 'reportó', 'correo', 'fecha', 'texto', 'nota de resolución',
    'plazo', 'responsable', 'resuelto', 'resolvió', 'tiempo de solución', 'respuestas', 'capturas',
    'esfuerzo (h)', 'se resuelve con',
];

const vinculo = (item) => [item.esfuerzo_horas ?? '', item.principal?.etiqueta ?? ''];

const fecha = (valor) => {
    if (!valor) return '';
    const d = new Date(valor);
    if (Number.isNaN(d.getTime())) return '';
    const dos = (n) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${dos(d.getMonth() + 1)}-${dos(d.getDate())} ${dos(d.getHours())}:${dos(d.getMinutes())}`;
};

const respuestas = (item) => (item.seguimiento ?? [])
    .filter((e) => e.accion === 'respuesta')
    .map((e) => `${fecha(e.creado)} · ${e.autor || e.autor_email}: ${e.texto}`)
    .join('\n');

const filaFalla = (proyecto, herramienta, f) => [
    proyecto, herramienta, f.tipo === 'no_pude' ? 'No pude probarlo' : 'Falla', f.id, f.ronda_nombre ?? f.ronda_id,
    f.caso_id, f.caso_titulo, f.seccion_titulo || f.seccion_id, pasoDeFalla(f),
    SEVERIDADES[f.severidad]?.texto ?? f.severidad, f.tipo === 'no_pude' ? '' : REPRODUCIBLE[f.reproducible] ?? '',
    ESTADOS_FALLA[f.estado]?.texto ?? f.estado, f.usuario_nombre ?? '', f.usuario_email, fecha(f.creada), f.obtenido,
    f.nota_resolucion, f.plazo ?? '', f.plazo_por_nombre || f.plazo_por || '', fecha(f.resuelta_en),
    f.resuelta_por_nombre || f.resuelta_por || '', duracion(f.creada, f.resuelta_en), respuestas(f), f.evidencias.length,
    ...vinculo(f),
];

const filaComentario = (proyecto, herramienta, c) => [
    proyecto, herramienta, 'Comentario', c.id ?? '', c.ronda_nombre, c.caso_id, c.caso_titulo, '',
    c.tipo === 'no_pude' ? 'No pudo probarlo' : `${c.paso + 1}. ${c.paso_texto}`, '', '',
    ESTADOS_COMENTARIO[c.estado]?.texto ?? c.estado ?? '', c.autor, c.usuario_email, fecha(c.creado ?? c.actualizado),
    c.comentario, '', c.plazo ?? '', c.plazo_por_nombre || c.plazo_por || '', fecha(c.resuelto_en),
    c.resuelto_por_nombre || c.resuelto_por || '', duracion(c.creado, c.resuelto_en), respuestas(c), '',
    ...vinculo(c),
];

const celda = (valor) => {
    const texto = valor === null || valor === undefined ? '' : String(valor);
    const seguro = PELIGROSOS.some((p) => texto.startsWith(p)) ? `'${texto}` : texto;
    return /[",\n\r]/.test(seguro) ? `"${seguro.replaceAll('"', '""')}"` : seguro;
};

const SIN_LETRAS = /[^a-z0-9]+/g;

export const nombreArchivo = (proyectos, fecha) => {
    const parte = proyectos.length === 1
        ? proyectos[0].normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().replace(SIN_LETRAS, '-').replace(/^-|-$/g, '')
        : 'varios-proyectos';
    return ['informe-fallas', parte, fecha].filter(Boolean).join('-');
};

export const csvInforme = (secciones) => {
    const filas = secciones.flatMap((s) => s.grupos.flatMap((g) => [
        ...g.fallas.map((f) => filaFalla(s.nombre, g.nombre, f)),
        ...g.comentarios.map((c) => filaComentario(s.nombre, g.nombre, c)),
    ]));
    return BOM + [COLUMNAS, ...filas].map((fila) => fila.map(celda).join(',')).join('\r\n');
};

export const descargarCsv = (texto, nombre) => {
    const url = URL.createObjectURL(new Blob([texto], { type: 'text/csv;charset=utf-8' }));
    const enlace = document.createElement('a');
    enlace.href = url;
    enlace.download = nombre;
    enlace.click();
    URL.revokeObjectURL(url);
};
