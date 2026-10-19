const PAGINAS = {
    '/': 'Inicio',
    '/tablero': 'Tablero',
    '/participacion': 'Participación',
    '/fallas': 'Fallas',
    '/herramientas': 'Herramientas',
    '/aprobaciones': 'Aprobaciones',
    '/rondas': 'Rondas',
    '/avisos': 'Avisos',
};

const nombreCaso = (p) => (p.caso_titulo ? `${p.caso_id} · ${p.caso_titulo}` : p.caso_id);

export const describirPresencia = (p) => {
    if (p.caso_id) {
        if (p.accion === 'reportando') return `Reportando una falla en ${nombreCaso(p)}`;
        if (p.accion === 'comentando') return `Comentando ${p.paso ? `el paso ${p.paso} de ` : ''}${nombreCaso(p)}`;
        if (p.paso) return `Paso ${p.paso} de ${nombreCaso(p)}`;
        return `Viendo ${nombreCaso(p)}`;
    }
    if (p.seccion_id) return `En la sección ${p.seccion_titulo || p.seccion_id}`;
    const pagina = PAGINAS[p.ruta.split(/[?#]/)[0]];
    return pagina ? `En ${pagina}` : `En ${p.ruta}`;
};

export const haceTiempo = (segundos) => {
    if (segundos < 60) return `hace ${Math.max(segundos, 1)} s`;
    return `hace ${Math.floor(segundos / 60)} min`;
};

export const enlacePresencia = (p, ruta = (r) => r) => {
    if (!p.caso_id) return null;
    const caso = `/caso/${encodeURIComponent(p.caso_id)}`;
    return ruta(p.paso ? `${caso}?paso=${p.paso}` : caso);
};
