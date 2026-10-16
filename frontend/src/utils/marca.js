export const tituloDocumento = (producto, nombre) => [producto, nombre].filter(Boolean).join(' · ');

export const etiquetaInicio = (producto, nombre) => {
    const titulo = tituloDocumento(producto, nombre);
    return titulo ? `${titulo}, ir a inicio` : 'Ir a inicio';
};
