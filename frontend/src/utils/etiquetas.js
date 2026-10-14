export const FAMILIAS = {
    A: 'Entorno y modos',
    B: 'Acceso y permisos',
    C: 'Funcional',
    D: 'Respaldos',
    E: 'Revisión final',
    T: 'Técnica',
};

export const ESTADOS_RESULTADO = {
    pendiente: { texto: 'Pendiente', tono: 'neutro' },
    pasa: { texto: 'Pasa', tono: 'exito' },
    falla: { texto: 'Falla', tono: 'error' },
    no_pude: { texto: 'No pude probarlo', tono: 'aviso' },
};

export const SEVERIDADES = {
    critica: { texto: 'Crítica', tono: 'error' },
    alta: { texto: 'Alta', tono: 'aviso' },
    media: { texto: 'Media', tono: 'marca' },
    baja: { texto: 'Baja', tono: 'neutro' },
};

export const ESTADOS_FALLA = {
    nueva: { texto: 'Nueva', tono: 'error' },
    en_curso: { texto: 'En curso', tono: 'aviso' },
    lista_para_revalidar: { texto: 'Lista para revalidar', tono: 'marca' },
    cerrada: { texto: 'Cerrada', tono: 'exito' },
};

export const MODOS = {
    prod: { texto: 'Modo producción', tono: 'marca' },
    beta: { texto: 'Modo prueba', tono: 'aviso' },
    dev: { texto: 'Modo desarrollo', tono: 'neutro' },
};

export const REPRODUCIBLE = {
    siempre: 'Siempre que lo intento',
    a_veces: 'A veces',
    una_vez: 'Solo una vez',
};

export const opciones = (mapa) => Object.entries(mapa).map(([valor, dato]) => ({
    valor,
    texto: typeof dato === 'string' ? dato : dato.texto,
}));

export const HOY = {
    prod: { texto: 'prod', tono: 'exito' },
    beta: { texto: 'solo beta', tono: 'aviso' },
    oculto: { texto: 'oculto', tono: 'neutro' },
};

export const DECISIONES = {
    desplegar: { texto: 'Desplegar', tono: 'exito' },
    desplegar_con_aviso: { texto: 'Desplegar con aviso', tono: 'aviso' },
    aplazar: { texto: 'Aplazar', tono: 'error' },
    pendiente: { texto: 'Sin recomendación', tono: 'neutro' },
};

export const SUGERENCIAS = {
    desplegar: { texto: 'Desplegar', tono: 'exito' },
    desplegar_con_aviso: { texto: 'Desplegar con aviso', tono: 'aviso' },
    aplazar: { texto: 'Aplazar', tono: 'error' },
    sin_probar: { texto: 'Sin probar', tono: 'neutro' },
};

export const APROBACIONES = {
    aprobada: { texto: 'Aprobada', tono: 'exito' },
    aprobada_parcial: { texto: 'Aprobada parcialmente', tono: 'aviso' },
    rechazada: { texto: 'Rechazada', tono: 'error' },
    pendiente: { texto: 'Pendiente', tono: 'neutro' },
};
