import { formatters, toPng, toSvg } from '@npmegar/tequio';

const formato = formatters('es');

const plural = (n, uno, varios) => `${n} ${n === 1 ? uno : varios}`;

export const ETIQUETAS = {
    title: (grafo) => {
        const proyectos = grafo.nodes.filter((n) => n.kind === 'project').length;
        return `Participación: ${plural(proyectos, 'proyecto', 'proyectos')} y ${plural(grafo.nodes.length - proyectos, 'persona', 'personas')}`;
    },
    project: (nodo, f, estados) => {
        const conteos = estados
            .filter((e) => (nodo.data.counts?.[e.key] ?? 0) > 0)
            .map((e) => `${f.metric(nodo.data.counts[e.key])} ${e.label.toLowerCase()}`);
        return [`${nodo.data.name}: ${f.percent(nodo.data.progress)} de avance`, ...conteos].join(', ');
    },
    person: (nodo, f) => {
        const n = nodo.data.metric ?? 0;
        return `${nodo.data.name}: ${f.metric(n)} ${n === 1 ? 'caso marcado' : 'casos marcados'}`;
    },
};

export const OPCIONES_IMPRESION = {
    theme: 'light',
    locale: 'es',
    labels: ETIQUETAS,
    layout: { width: 1600, height: 1000 },
};

const paraImprimir = (datos) => ({ ...datos, people: datos.people.map((p) => ({ ...p, active: true })) });

export const svgParticipacion = (datos) => toSvg(paraImprimir(datos), OPCIONES_IMPRESION);

export const descargarParticipacion = async (datos, formatoArchivo, nombre) => {
    const blob = formatoArchivo === 'png'
        ? await toPng(paraImprimir(datos), { ...OPCIONES_IMPRESION, scale: 2 })
        : new Blob([svgParticipacion(datos)], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const enlace = document.createElement('a');
    enlace.href = url;
    enlace.download = `${nombre}.${formatoArchivo}`;
    enlace.click();
    URL.revokeObjectURL(url);
};

export const porcentaje = (valor) => formato.percent(valor);
