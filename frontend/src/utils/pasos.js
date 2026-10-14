export const normalizarPasos = (lista = []) => lista.map((p) => (
    typeof p === 'number' ? { paso: p, estado: 'pasa', comentario: null } : { comentario: null, ...p }
));

export const conRespuesta = (pasos, respuesta) => [
    ...pasos.filter((p) => p.paso !== respuesta.paso),
    respuesta,
].sort((a, b) => a.paso - b.paso);

export const estadoDelCaso = (pasos, total) => {
    if (pasos.some((p) => p.estado === 'falla')) return 'falla';
    if (pasos.some((p) => p.estado === 'no_pude')) return 'no_pude';
    return pasos.length >= total ? 'pasa' : 'pendiente';
};

export const siguienteSinResponder = (pasos, total, desde = 0) => {
    const respondidos = new Set(pasos.map((p) => p.paso));
    const orden = [...Array(total).keys()];
    const despues = [...orden.slice(desde + 1), ...orden.slice(0, desde + 1)];
    return despues.find((i) => !respondidos.has(i)) ?? null;
};

export const pasoInicial = (pasos, total) => {
    const pendiente = siguienteSinResponder(pasos, total, -1);
    return pendiente ?? 0;
};
