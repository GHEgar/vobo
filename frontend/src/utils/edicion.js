export const CLAVE_EDICION = 'validacion.modo-edicion';

export const apagarEdicion = () => {
    try {
        window.sessionStorage.removeItem(CLAVE_EDICION);
    } catch {
        return;
    }
};

export const enlaceEditor = (seccionId) => (seccionId ? `/editor?seccion=${encodeURIComponent(seccionId)}` : '/editor');

export const idCopia = (id, existentes) => {
    const base = `${id}-COPIA`;
    if (!existentes.includes(base)) return base;
    let n = 2;
    while (existentes.includes(`${base}-${n}`)) n += 1;
    return `${base}-${n}`;
};

export const contornoEdicion = (activo) => (activo ? 'group/edicion relative outline-2 outline-dashed -outline-offset-2 outline-aviso/70' : '');
