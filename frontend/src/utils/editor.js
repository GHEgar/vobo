export const HERRAMIENTA_GENERAL = 'general';

export const ruta = (loc) => loc.join('.');

export const erroresDe = (error) => new Map((error?.detalle ?? []).map((e) => [ruta(e.loc), e.msg]));

export const conPrefijo = (errores, prefijo) => new Map(
    [...errores].filter(([clave]) => clave.startsWith(`${prefijo}.`)).map(([clave, msg]) => [clave.slice(prefijo.length + 1), msg]),
);

export const mover = (lista, indice, delta) => {
    const destino = indice + delta;
    if (destino < 0 || destino >= lista.length) return lista;
    const copia = [...lista];
    [copia[indice], copia[destino]] = [copia[destino], copia[indice]];
    return copia;
};

export const intercambiar = (ids, a, b) => {
    const copia = [...ids];
    const i = copia.indexOf(a);
    const j = copia.indexOf(b);
    [copia[i], copia[j]] = [copia[j], copia[i]];
    return copia;
};

export const herramientaGeneral = () => ({ id: HERRAMIENTA_GENERAL, nombre: 'General', hoy: 'prod' });

export const seccionVacia = (sistema = '') => ({
    id: '',
    titulo: '',
    sistema,
    audiencia: 'funcional',
    resumen: '',
    que_cambia: [],
    donde: '',
    herramientas: [herramientaGeneral()],
    media: [],
    casos: [],
});

export const pasoVacio = () => ({ texto: '', procedimiento: null });

export const casoVacio = (herramienta = HERRAMIENTA_GENERAL) => ({
    id: '',
    familia: 'C',
    herramienta,
    titulo: '',
    rol: '',
    cuenta: '',
    modo: 'prod',
    antes: '',
    pasos: [pasoVacio()],
    esperado: '',
    severidad: 'media',
});

export const procedimientoVacio = () => ({ id: '', titulo: '', descripcion: '', pasos: [] });

export const tamanoLegible = (bytes) => (bytes >= 1024 * 1024 ? `${(bytes / 1024 / 1024).toFixed(1)} MB` : `${Math.ceil(bytes / 1024)} KB`);

export const ACCIONES = {
    crear: 'Creación',
    editar: 'Edición',
    borrar: 'Borrado',
    importar: 'Importación',
    restaurar: 'Restauración',
    ordenar: 'Cambio de orden',
    ocultar: 'Se ocultó',
    mostrar: 'Se mostró',
    subir: 'Animación subida',
    reemplazar: 'Animación reemplazada',
};
