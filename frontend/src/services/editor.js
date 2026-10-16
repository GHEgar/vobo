import { consulta, solicitar } from '@/services/api';
import { conProyecto } from '@/utils/enlaces';

const seccion = (id) => `/editor/secciones/${encodeURIComponent(id)}`;
const procedimiento = (id) => `/editor/procedimientos/${encodeURIComponent(id)}`;

const conArchivo = (archivo) => {
    const form = new FormData();
    form.append('archivo', archivo);
    return form;
};

export const urlExportar = (proyecto) => `/api/contenido/exportar.zip${consulta({ proyecto })}`;

export const nuevoServicio = (proyecto) => {
    const en = (ruta, opciones) => solicitar(conProyecto(ruta, proyecto), opciones);
    return {
        fetchEstado: () => en('/editor/estado'),
        fetchSecciones: () => en('/editor/secciones'),
        fetchSeccion: (id) => en(seccion(id)),
        crearSeccion: (datos) => en('/editor/secciones', { method: 'POST', json: { datos } }),
        guardarSeccion: ({ id, datos }) => en(seccion(id), { method: 'PUT', json: { datos } }),
        borrarSeccion: (id) => en(seccion(id), { method: 'DELETE' }),
        ocultarSeccion: ({ id, oculta }) => en(`${seccion(id)}/oculta`, { method: 'PUT', json: { oculta } }),
        duplicarSeccion: ({ id, nuevo }) => en(`${seccion(id)}/duplicar`, { method: 'POST', json: { id: nuevo } }),
        ordenarSecciones: (ids) => en('/editor/secciones/orden', { method: 'PUT', json: { ids } }),
        fetchProcedimientos: () => en('/editor/procedimientos'),
        crearProcedimiento: (datos) => en('/editor/procedimientos', { method: 'POST', json: { datos } }),
        guardarProcedimiento: ({ id, datos }) => en(procedimiento(id), { method: 'PUT', json: { datos } }),
        borrarProcedimiento: (id) => en(procedimiento(id), { method: 'DELETE' }),
        subirAnimacion: ({ id, archivo }) => en(`${procedimiento(id)}/media`, { method: 'PUT', form: conArchivo(archivo) }),
        quitarAnimacion: (id) => en(`${procedimiento(id)}/media`, { method: 'DELETE' }),
        fetchHistorial: ({ tipo, id }) => en(`/editor/historial/${tipo}/${encodeURIComponent(id)}`),
        restaurarVersion: (id) => en(`/editor/historial/${id}/restaurar`, { method: 'POST' }),
        importarPaquete: ({ archivo, confirmar }) => en(`/editor/importar?confirmar=${confirmar}`, {
            method: 'POST',
            form: conArchivo(archivo),
            espera: 300000,
        }),
    };
};
