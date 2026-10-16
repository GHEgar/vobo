const normalizar = (texto) => (texto ?? '').normalize('NFD').replace(/\p{M}/gu, '').replace(/\s+/g, ' ').trim().toLowerCase();

export const mismoNombre = (a, b) => normalizar(a) === normalizar(b);

export const tituloDocumento = (producto, nombre) => [producto, mismoNombre(producto, nombre) ? '' : nombre].filter(Boolean).join(' · ');

export const etiquetaInicio = (producto, nombre) => {
    const titulo = tituloDocumento(producto, nombre);
    return titulo ? `${titulo}, ir a inicio` : 'Ir a inicio';
};

export const nombreVisible = (producto, proyecto, proyectos) => {
    if (!proyecto) return '';
    return proyectos.length < 2 && mismoNombre(proyecto.nombre, producto) ? '' : proyecto.nombre;
};
