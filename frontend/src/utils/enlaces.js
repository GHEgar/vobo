export const PARAMETRO_PROYECTO = 'proyecto';

export const conProyecto = (ruta, clave) => {
    if (!clave) return ruta;
    const [base, ancla = ''] = ruta.split('#');
    const [camino, busqueda = ''] = base.split('?');
    const params = new URLSearchParams(busqueda);
    params.set(PARAMETRO_PROYECTO, clave);
    return `${camino}?${params}${ancla ? `#${ancla}` : ''}`;
};

export const claveDeEnlace = (clave, proyectos) => {
    const proyecto = proyectos.find((p) => p.clave === clave);
    return proyecto && !proyecto.por_omision ? proyecto.clave : null;
};
