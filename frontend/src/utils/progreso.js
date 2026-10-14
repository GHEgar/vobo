import { normalizarPasos, pasoInicial } from '@/utils/pasos';

export const indexarContenido = (contenido) => {
    const casos = new Map();
    const secciones = new Map();
    const procedimientos = new Map(contenido.procedimientos.map((p) => [p.id, p]));
    contenido.secciones.forEach((seccion) => {
        secciones.set(seccion.id, seccion);
        seccion.casos.forEach((caso) => casos.set(caso.id, { ...caso, seccionId: seccion.id }));
    });
    return { contenido, casos, secciones, procedimientos };
};

const contar = (casos, estados) => {
    const hechos = casos.filter((c) => (estados.get(c.id)?.estado ?? 'pendiente') !== 'pendiente').length;
    return { hechos, total: casos.length };
};

const esVisible = (seccion, mis, asignadas) => {
    if (mis?.secciones_visibles) return mis.secciones_visibles.includes(seccion.id);
    if (seccion.audiencia === 'tecnica') return asignadas.has(seccion.id);
    return asignadas.size === 0 || asignadas.has(seccion.id);
};

export const resumirProgreso = (indice, mis, audiencia = null) => {
    const estados = new Map((mis?.resultados ?? []).map((r) => [r.caso_id, r]));
    const asignadas = new Set(mis?.secciones_asignadas ?? []);
    const secciones = indice.contenido.secciones
        .filter((s) => esVisible(s, mis, asignadas))
        .filter((s) => !audiencia || s.audiencia === audiencia)
        .map((s) => ({ ...s, progreso: contar(s.casos, estados) }));
    const casos = secciones.flatMap((s) => s.casos.map((c) => ({ ...c, seccionId: s.id })));
    const siguiente = casos.find((c) => (estados.get(c.id)?.estado ?? 'pendiente') === 'pendiente') ?? null;
    return {
        estados,
        secciones,
        casos,
        siguiente,
        total: contar(casos, estados),
        asignadas: asignadas.size > 0,
        veTecnico: Boolean(mis?.ve_tecnico),
    };
};

export const estadoDe = (estados, casoId) => estados.get(casoId)?.estado ?? 'pendiente';

export const casoParaContinuar = (datos) => {
    const enCurso = datos.casos
        .map((caso) => ({ caso, resultado: datos.estados.get(caso.id) }))
        .filter(({ resultado }) => resultado?.estado === 'pendiente' && resultado.pasos_marcados?.length)
        .sort((a, b) => String(b.resultado.actualizado).localeCompare(String(a.resultado.actualizado)))[0];
    if (enCurso) {
        const pasos = normalizarPasos(enCurso.resultado.pasos_marcados);
        return { caso: enCurso.caso, paso: pasoInicial(pasos, enCurso.caso.pasos.length), enCurso: true };
    }
    return datos.siguiente ? { caso: datos.siguiente, paso: 0, enCurso: false } : null;
};
