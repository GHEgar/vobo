const indiceDe = (proyectos) => new Map(proyectos.map((p, i) => [p.clave, i]));

export const nombreProyecto = (proyectos, clave) => proyectos.find((p) => p.clave === clave)?.nombre ?? clave;

export const ordenarProyectos = (proyectos, claves) => {
    const orden = indiceDe(proyectos);
    const posicion = (clave) => orden.get(clave) ?? proyectos.length;
    return [...claves].sort((a, b) => posicion(a) - posicion(b));
};

export const seccionesPorProyecto = (proyectos, secciones) => ordenarProyectos(proyectos, [...new Set(secciones.map((s) => s.sistema))])
    .map((clave) => ({ clave, nombre: nombreProyecto(proyectos, clave), secciones: secciones.filter((s) => s.sistema === clave) }));

export const agruparPorProyecto = (proyectos, secciones) => {
    const grupos = new Map();
    secciones.forEach((s) => {
        const grupo = grupos.get(s.sistema) ?? { clave: s.sistema, nombre: nombreProyecto(proyectos, s.sistema), secciones: [], hechos: 0, total: 0 };
        grupo.secciones.push(s);
        grupo.hechos += s.progreso.hechos;
        grupo.total += s.progreso.total;
        grupos.set(s.sistema, grupo);
    });
    return ordenarProyectos(proyectos, [...grupos.keys()]).map((clave) => grupos.get(clave));
};
