import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import * as api from '@/services/validacion';
import { useClaveProyecto } from '@/hooks/useProyecto';

const MINUTO = 60 * 1000;

export const useProyectosLista = () => useQuery({
    queryKey: ['proyectos'],
    queryFn: api.fetchProyectos,
    staleTime: MINUTO,
});

export const useContenido = () => {
    const proyecto = useClaveProyecto();
    return useQuery({
        queryKey: ['contenido', proyecto],
        queryFn: () => api.fetchContenido(proyecto),
        staleTime: MINUTO,
    });
};

export const useRondas = () => {
    const proyecto = useClaveProyecto();
    return useQuery({
        queryKey: ['rondas', proyecto],
        queryFn: () => api.fetchRondas(proyecto),
        staleTime: MINUTO,
    });
};

export const useMisCasos = (rondaId) => useQuery({
    queryKey: ['mis-casos', { rondaId, proyecto: useClaveProyecto() }],
    queryFn: () => api.fetchMisCasos(rondaId),
    enabled: Boolean(rondaId),
    staleTime: 15 * 1000,
});

export const useTablero = (rondaId, audiencia = 'todas') => useQuery({
    queryKey: ['tablero', { rondaId, audiencia, proyecto: useClaveProyecto() }],
    queryFn: () => api.fetchTablero(rondaId, audiencia),
    enabled: Boolean(rondaId),
    refetchInterval: MINUTO,
});

export const useFallas = (filtros) => {
    const proyecto = useClaveProyecto();
    const conProyecto = { ...filtros, proyecto };
    return useQuery({
        queryKey: ['fallas', conProyecto],
        queryFn: () => api.fetchFallas(conProyecto),
        staleTime: 15 * 1000,
    });
};

export const useHerramientas = (rondaId) => useQuery({
    queryKey: ['herramientas', { rondaId, proyecto: useClaveProyecto() }],
    queryFn: () => api.fetchHerramientas(rondaId),
    enabled: Boolean(rondaId),
    staleTime: 30 * 1000,
});

export const useComentarios = (rondaId) => {
    const proyecto = useClaveProyecto();
    return useQuery({
        queryKey: ['comentarios', { rondaId, proyecto }],
        queryFn: () => api.fetchComentarios(rondaId, proyecto),
        staleTime: 15 * 1000,
    });
};

export const useAccesos = () => useQuery({ queryKey: ['accesos'], queryFn: api.fetchAccesos });

export const useComentariosCaso = (casoId, rondaId) => useQuery({
    queryKey: ['comentarios', 'caso', { casoId, rondaId, proyecto: useClaveProyecto() }],
    queryFn: () => api.fetchComentariosCaso(casoId, rondaId),
    enabled: Boolean(rondaId),
});

export const useCuentasPrueba = (rondaId) => useQuery({
    queryKey: ['cuentas-prueba', rondaId, useClaveProyecto()],
    queryFn: () => api.fetchCuentasPrueba(rondaId),
    staleTime: 10 * MINUTO,
    retry: false,
});

export const useAprobaciones = (rondaId) => useQuery({
    queryKey: ['aprobaciones', { rondaId, proyecto: useClaveProyecto() }],
    queryFn: () => api.fetchAprobaciones(rondaId),
    enabled: Boolean(rondaId),
    staleTime: 15 * 1000,
});

export const useUsuarios = () => useQuery({ queryKey: ['usuarios'], queryFn: api.fetchUsuarios });

export const useAsignaciones = (rondaId) => useQuery({
    queryKey: ['asignaciones', { rondaId, proyecto: useClaveProyecto() }],
    queryFn: () => api.fetchAsignaciones(rondaId),
    enabled: Boolean(rondaId),
});

export const usePresentes = () => {
    const proyecto = useClaveProyecto();
    return useQuery({
        queryKey: ['presencia', proyecto],
        queryFn: () => api.fetchPresencia(proyecto),
        refetchInterval: 30 * 1000,
    });
};

const useMutacion = (mutationFn, claves) => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn,
        onSuccess: () => Promise.all(
            claves.map((clave) => queryClient.invalidateQueries({ queryKey: [clave] })),
        ),
    });
};

export const useGuardarResultado = () => useMutacion(api.guardarResultado, ['mis-casos', 'tablero', 'herramientas', 'comentarios']);
export const useReportarFalla = () => useMutacion(api.reportarFalla, ['mis-casos', 'tablero', 'fallas', 'herramientas']);
export const useActualizarFalla = () => useMutacion(api.actualizarFalla, ['fallas', 'tablero', 'herramientas']);
export const useCrearRonda = () => {
    const proyecto = useClaveProyecto();
    return useMutacion((datos) => api.crearRonda({ ...datos, proyecto }), ['rondas']);
};
export const useActualizarRonda = () => useMutacion(api.actualizarRonda, ['rondas']);
export const useBorrarRonda = () => useMutacion(api.borrarRonda, ['rondas', 'mis-casos', 'tablero', 'fallas', 'herramientas', 'comentarios']);
export const useGuardarAsignaciones = () => useMutacion(api.guardarAsignaciones, ['asignaciones', 'mis-casos', 'tablero', 'cuentas-prueba']);
export const useDecidirHerramienta = () => useMutacion(api.decidirHerramienta, ['herramientas', 'tablero']);
export const useGuardarAccesos = () => useMutacion(api.guardarAccesos, ['accesos', 'sesion']);
export const useRegistrarAprobaciones = () => useMutacion(api.registrarAprobaciones, ['aprobaciones']);
