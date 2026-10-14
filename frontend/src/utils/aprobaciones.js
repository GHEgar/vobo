import { nombreProyecto, ordenarProyectos } from '@/utils/proyectos';

export const FILTROS = [
    { clave: 'pendientes', texto: 'Pendientes', acepta: (e) => e === 'pendiente' },
    { clave: 'aprobadas', texto: 'Aprobadas', acepta: (e) => e === 'aprobada' || e === 'aprobada_parcial' },
    { clave: 'rechazadas', texto: 'Rechazadas', acepta: (e) => e === 'rechazada' },
    { clave: 'todas', texto: 'Todas', acepta: () => true },
];

export const animacionDe = (indice, casoId) => {
    const caso = indice.casos.get(casoId);
    const paso = caso?.pasos.find((p) => indice.procedimientos.get(p.procedimiento)?.url);
    return paso ? indice.procedimientos.get(paso.procedimiento) : null;
};

export const combinar = (herramientas, aprobaciones) => {
    const estados = new Map((aprobaciones?.herramientas ?? []).map((h) => [h.herramienta_id, h]));
    return herramientas.map((h) => {
        const aprobacion = estados.get(h.id);
        const porCaso = new Map((aprobacion?.caracteristicas ?? []).map((c) => [c.caso_id, c]));
        return {
            ...h,
            aprobacion: aprobacion ?? { estado: 'pendiente', actual: null, historial: [] },
            caracteristicas: h.caracteristicas.map((c) => ({ ...c, aprobacion: porCaso.get(c.caso_id) ?? { estado: 'pendiente', actual: null } })),
        };
    });
};

export const agruparPorSistema = (proyectos, items) => ordenarProyectos(proyectos, [...new Set(items.map((h) => h.sistema))])
    .map((clave) => ({ clave, nombre: nombreProyecto(proyectos, clave), herramientas: items.filter((h) => h.sistema === clave) }));

export const contar = (items) => FILTROS.reduce((cuentas, f) => ({ ...cuentas, [f.clave]: items.filter((h) => f.acepta(h.aprobacion.estado)).length }), {});
