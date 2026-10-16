import { useMemo } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { nuevoServicio } from '@/services/editor';
import { useClaveProyecto } from '@/hooks/useProyecto';

const TODO = [['editor'], ['contenido'], ['instancia'], ['mis-casos'], ['tablero'], ['herramientas']];

const useServicio = () => {
    const proyecto = useClaveProyecto();
    const api = useMemo(() => nuevoServicio(proyecto), [proyecto]);
    return { api, proyecto };
};

const useMutacion = (elegir) => {
    const queryClient = useQueryClient();
    const { api } = useServicio();
    return useMutation({
        mutationFn: elegir(api),
        onSuccess: () => TODO.forEach((queryKey) => queryClient.invalidateQueries({ queryKey })),
    });
};

const useConsulta = (clave, elegir, enabled = true) => {
    const { api, proyecto } = useServicio();
    return useQuery({ queryKey: ['editor', proyecto, ...clave], queryFn: elegir(api), enabled });
};

export const useEstadoEditor = (habilitado = true) => useConsulta(['estado'], (api) => api.fetchEstado, habilitado);

export const useSeccionesEditor = (habilitado = true) => useConsulta(['secciones'], (api) => api.fetchSecciones, habilitado);
export const useSeccionEditor = (id) => useConsulta(['secciones', id], (api) => () => api.fetchSeccion(id), Boolean(id));
export const useProcedimientosEditor = (habilitado = true) => useConsulta(['procedimientos'], (api) => api.fetchProcedimientos, habilitado);
export const useHistorial = (tipo, id) => useConsulta(['historial', tipo, id], (api) => () => api.fetchHistorial({ tipo, id }), Boolean(id));

export const useCrearSeccion = () => useMutacion((api) => api.crearSeccion);
export const useGuardarSeccion = () => useMutacion((api) => api.guardarSeccion);
export const useBorrarSeccion = () => useMutacion((api) => api.borrarSeccion);
export const useOcultarSeccion = () => useMutacion((api) => api.ocultarSeccion);
export const useDuplicarSeccion = () => useMutacion((api) => api.duplicarSeccion);
export const useOrdenarSecciones = () => useMutacion((api) => api.ordenarSecciones);

export const useCrearProcedimiento = () => useMutacion((api) => api.crearProcedimiento);
export const useGuardarProcedimiento = () => useMutacion((api) => api.guardarProcedimiento);
export const useBorrarProcedimiento = () => useMutacion((api) => api.borrarProcedimiento);
export const useSubirAnimacion = () => useMutacion((api) => api.subirAnimacion);
export const useQuitarAnimacion = () => useMutacion((api) => api.quitarAnimacion);

export const useRestaurarVersion = () => useMutacion((api) => api.restaurarVersion);
export const useImportarPaquete = () => useMutacion((api) => api.importarPaquete);
