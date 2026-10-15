import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import * as api from '@/services/validacion';

const MINUTO = 60 * 1000;

export const useContenido = () => useQuery({
    queryKey: ['contenido'],
    queryFn: api.fetchContenido,
    staleTime: MINUTO,
});

export const useRondas = () => useQuery({
    queryKey: ['rondas'],
    queryFn: api.fetchRondas,
    staleTime: MINUTO,
});

export const useMisCasos = (rondaId) => useQuery({
    queryKey: ['mis-casos', { rondaId }],
    queryFn: () => api.fetchMisCasos(rondaId),
    enabled: Boolean(rondaId),
    staleTime: 15 * 1000,
});

export const useTablero = (rondaId, audiencia = 'todas') => useQuery({
    queryKey: ['tablero', { rondaId, audiencia }],
    queryFn: () => api.fetchTablero(rondaId, audiencia),
    enabled: Boolean(rondaId),
    refetchInterval: MINUTO,
});

export const useFallas = (filtros) => useQuery({
    queryKey: ['fallas', filtros],
    queryFn: () => api.fetchFallas(filtros),
    staleTime: 15 * 1000,
});

export const useHerramientas = (rondaId) => useQuery({
    queryKey: ['herramientas', { rondaId }],
    queryFn: () => api.fetchHerramientas(rondaId),
    enabled: Boolean(rondaId),
    staleTime: 30 * 1000,
});

export const useComentarios = (rondaId) => useQuery({
    queryKey: ['comentarios', { rondaId }],
    queryFn: () => api.fetchComentarios(rondaId),
    staleTime: 15 * 1000,
});

export const useAccesos = () => useQuery({ queryKey: ['accesos'], queryFn: api.fetchAccesos });

export const useComentariosCaso = (casoId, rondaId) => useQuery({
    queryKey: ['comentarios', 'caso', { casoId, rondaId }],
    queryFn: () => api.fetchComentariosCaso(casoId, rondaId),
    enabled: Boolean(rondaId),
});

export const useCuentasPrueba = (rondaId) => useQuery({
    queryKey: ['cuentas-prueba', rondaId],
    queryFn: () => api.fetchCuentasPrueba(rondaId),
    staleTime: 10 * MINUTO,
    retry: false,
});

export const useAprobaciones = (rondaId) => useQuery({
    queryKey: ['aprobaciones', { rondaId }],
    queryFn: () => api.fetchAprobaciones(rondaId),
    enabled: Boolean(rondaId),
    staleTime: 15 * 1000,
});

export const useUsuarios = () => useQuery({ queryKey: ['usuarios'], queryFn: api.fetchUsuarios });

export const useAsignaciones = (rondaId) => useQuery({
    queryKey: ['asignaciones', { rondaId }],
    queryFn: () => api.fetchAsignaciones(rondaId),
    enabled: Boolean(rondaId),
});

export const usePresentes = () => useQuery({
    queryKey: ['presencia'],
    queryFn: api.fetchPresencia,
    refetchInterval: 30 * 1000,
});

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
export const useCrearRonda = () => useMutacion(api.crearRonda, ['rondas']);
export const useActualizarRonda = () => useMutacion(api.actualizarRonda, ['rondas']);
export const useBorrarRonda = () => useMutacion(api.borrarRonda, ['rondas', 'mis-casos', 'tablero', 'fallas', 'herramientas', 'comentarios']);
export const useGuardarAsignaciones = () => useMutacion(api.guardarAsignaciones, ['asignaciones', 'mis-casos', 'tablero', 'cuentas-prueba']);
export const useDecidirHerramienta = () => useMutacion(api.decidirHerramienta, ['herramientas', 'tablero']);
export const useGuardarAccesos = () => useMutacion(api.guardarAccesos, ['accesos', 'sesion']);
export const useRegistrarAprobaciones = () => useMutacion(api.registrarAprobaciones, ['aprobaciones']);
