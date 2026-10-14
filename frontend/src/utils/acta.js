import { APROBACIONES, DECISIONES, SUGERENCIAS } from '@/utils/etiquetas';
import { formatearFecha } from '@/utils/formato';

export const recomendacionDe = (h) => {
    if (h.decision && h.decision.decision !== 'pendiente') {
        return { texto: DECISIONES[h.decision.decision].texto, motivo: h.decision.motivo || '' };
    }
    return { texto: `${SUGERENCIAS[h.sugerencia].texto} (sugerida)`, motivo: h.sugerencia_motivo };
};

export const evidenciaDe = (h) => {
    const abiertas = Object.values(h.fallas_abiertas).reduce((n, v) => n + v, 0);
    return `${h.casos.pasa} pasa · ${h.casos.falla} falla · ${h.casos.no_pude} no pude · ${abiertas} falla(s) abierta(s)`;
};

export const aprobacionDe = (h) => {
    const actual = h.aprobacion.actual;
    return {
        estado: APROBACIONES[h.aprobacion.estado].texto,
        quien: actual ? actual.usuario_nombre || actual.usuario_email : '',
        fecha: actual ? formatearFecha(actual.creada) : '',
        comentario: actual?.comentario ?? '',
    };
};

export const pendientesORechazadas = (h) => h.caracteristicas.filter((c) => c.aprobacion.estado !== 'aprobada');

const celda = (texto) => String(texto ?? '').replaceAll('|', '\\|').replaceAll('\n', ' ');

export const actaMarkdown = ({ nombre, ronda, grupos, generada }) => {
    const lineas = [
        nombre ? `# Acta de aprobación · ${nombre}` : '# Acta de aprobación',
        '',
        `Ronda: ${ronda.nombre}${ronda.snapshot ? ` (${ronda.snapshot})` : ''} · Generada: ${generada}`,
    ];
    grupos.forEach((g) => {
        lineas.push('', `## ${g.nombre}`, '', '| Herramienta | Recomendación | Motivo | Evidencia | Aprobación |', '|---|---|---|---|---|');
        g.herramientas.forEach((h) => {
            const r = recomendacionDe(h);
            const a = aprobacionDe(h);
            const aprobacion = [a.estado, a.quien, a.fecha, a.comentario].filter(Boolean).join(' · ');
            lineas.push(`| ${celda(h.nombre)} | ${celda(r.texto)} | ${celda(r.motivo)} | ${celda(evidenciaDe(h))} | ${celda(aprobacion)} |`);
            pendientesORechazadas(h).forEach((c) => {
                lineas.push(`| ↳ ${celda(c.titulo)} (${c.caso_id}) |  |  |  | ${celda(APROBACIONES[c.aprobacion.estado].texto)} |`);
            });
        });
    });
    return `${lineas.join('\n')}\n`;
};
