export const hora = (fecha) => `${String(fecha.getHours()).padStart(2, '0')}:${String(fecha.getMinutes()).padStart(2, '0')}`;

export const haceCuanto = (iso, ahora) => {
    const minutos = Math.floor((ahora - new Date(iso).getTime()) / 60000);
    if (minutos < 1) return 'ahora';
    if (minutos < 60) return `hace ${minutos} min`;
    const horas = Math.floor(minutos / 60);
    if (horas < 24) return `hace ${horas} h`;
    return `hace ${Math.floor(horas / 24)} d`;
};

export const porcentaje = (fraccion) => `${Math.round((fraccion || 0) * 100)}%`;

export const plural = (n, uno, varios) => `${n} ${n === 1 ? uno : varios}`;

export const enGrupos = (lista, tamano) => {
    const grupos = [];
    for (let i = 0; i < lista.length; i += tamano) grupos.push(lista.slice(i, i + tamano));
    return grupos;
};

export const VISTAS = ['general', 'grafo'];

export const NOMBRES_VISTA = { general: 'General: anillos por proyecto', grafo: 'Grafo en vivo' };
