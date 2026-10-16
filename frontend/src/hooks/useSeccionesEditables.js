import { useMemo } from 'react';
import { useSeccionesEditor } from '@/hooks/useEditor';

const SIN_PROGRESO = { hechos: 0, total: 0 };

const oculta = (s) => ({ id: s.id, titulo: s.titulo, sistema: s.sistema, audiencia: s.audiencia, oculta: true, casos: [], progreso: SIN_PROGRESO, edicion: s });

export const useSeccionesEditables = (secciones, activo) => {
    const editor = useSeccionesEditor(activo);
    const resumen = activo ? editor.data : null;

    return useMemo(() => {
        if (!resumen || !secciones) return { secciones, ids: [] };
        const porId = new Map(resumen.map((s) => [s.id, s]));
        const visibles = new Set(secciones.map((s) => s.id));
        const orden = new Map(resumen.map((s, i) => [s.id, i]));
        const posicion = (s) => orden.get(s.id) ?? resumen.length;
        const todas = [
            ...secciones.map((s) => ({ ...s, edicion: porId.get(s.id) })),
            ...resumen.filter((s) => s.oculta && !visibles.has(s.id)).map(oculta),
        ].sort((a, b) => posicion(a) - posicion(b));
        return { secciones: todas, ids: resumen.map((s) => s.id) };
    }, [secciones, resumen]);
};
