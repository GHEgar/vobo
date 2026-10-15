import { ESTADOS_FALLA, SEVERIDADES } from '@/utils/etiquetas';

export const CAMPOS_FILTRO = ['ronda', 'tipo', 'sistema', 'severidad', 'estado'];

const TIPOS = { falla: 'Fallas', no_pude: 'No pude probarlo' };

export const filtrosDe = (params) => Object.fromEntries(CAMPOS_FILTRO.map((c) => [c, params.get(c) ?? '']));

export const zonaHoraria = () => Intl.DateTimeFormat().resolvedOptions().timeZone;

export const describirFiltros = (filtros, ronda) => [
    ['Ronda', ronda?.nombre ?? (filtros.ronda ? `#${filtros.ronda}` : 'Todas')],
    ['Tipo', TIPOS[filtros.tipo] ?? 'Todos'],
    ['Sistema', filtros.sistema || 'Todos'],
    ['Severidad', SEVERIDADES[filtros.severidad]?.texto ?? 'Todas'],
    ['Estado', ESTADOS_FALLA[filtros.estado]?.texto ?? 'Todos'],
];

const contar = (fallas, clave, etiqueta) => {
    const cuentas = new Map();
    fallas.forEach((f) => {
        const valor = clave(f);
        cuentas.set(valor, (cuentas.get(valor) ?? 0) + 1);
    });
    return [...cuentas].map(([valor, total]) => ({ valor, texto: etiqueta(valor), total }));
};

const enOrden = (mapa) => (filas) => filas.sort((a, b) => Object.keys(mapa).indexOf(a.valor) - Object.keys(mapa).indexOf(b.valor));

export const resumenFallas = (fallas) => ({
    severidad: enOrden(SEVERIDADES)(contar(fallas, (f) => f.severidad, (v) => SEVERIDADES[v]?.texto ?? v)),
    estado: enOrden(ESTADOS_FALLA)(contar(fallas, (f) => f.estado, (v) => ESTADOS_FALLA[v]?.texto ?? v)),
    seccion: contar(fallas, (f) => f.seccion_titulo || f.seccion_id || 'Sin sección', (v) => v)
        .sort((a, b) => b.total - a.total || a.texto.localeCompare(b.texto, 'es')),
});

export const pasoDeFalla = (falla) => (falla.paso === null ? 'Fuera de los pasos' : `${falla.paso + 1}. ${falla.paso_texto}`);
