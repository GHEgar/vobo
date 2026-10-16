const indiceDe = (sistemas) => new Map(sistemas.map((p, i) => [p.clave, i]));

export const nombreSistema = (sistemas, clave) => sistemas.find((p) => p.clave === clave)?.nombre ?? clave;

export const ordenarSistemas = (sistemas, claves) => {
    const orden = indiceDe(sistemas);
    const posicion = (clave) => orden.get(clave) ?? sistemas.length;
    return [...claves].sort((a, b) => posicion(a) - posicion(b));
};

export const seccionesPorSistema = (sistemas, secciones) => ordenarSistemas(sistemas, [...new Set(secciones.map((s) => s.sistema))])
    .map((clave) => ({ clave, nombre: nombreSistema(sistemas, clave), secciones: secciones.filter((s) => s.sistema === clave) }));

export const agruparSeccionesPorSistema = (sistemas, secciones) => {
    const grupos = new Map();
    secciones.forEach((s) => {
        const grupo = grupos.get(s.sistema) ?? { clave: s.sistema, nombre: nombreSistema(sistemas, s.sistema), secciones: [], hechos: 0, total: 0 };
        grupo.secciones.push(s);
        grupo.hechos += s.progreso.hechos;
        grupo.total += s.progreso.total;
        grupos.set(s.sistema, grupo);
    });
    return ordenarSistemas(sistemas, [...grupos.keys()]).map((clave) => grupos.get(clave));
};
