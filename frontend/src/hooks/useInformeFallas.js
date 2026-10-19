import { useQueries, useQuery } from '@tanstack/react-query';
import * as api from '@/services/validacion';

const VIGENCIA = 15 * 1000;

export const useRondasDe = (clave, activo) => useQuery({
    queryKey: ['rondas', clave],
    queryFn: () => api.fetchRondas(clave),
    enabled: Boolean(clave) && activo,
    staleTime: 60 * 1000,
});

export const useDatosInforme = (claves, ronda, conComentarios) => {
    const fallas = useQueries({
        queries: claves.map((proyecto) => ({
            queryKey: ['fallas', { ronda, proyecto }],
            queryFn: () => api.fetchFallas({ ronda, proyecto }),
            staleTime: VIGENCIA,
        })),
    });
    const comentarios = useQueries({
        queries: claves.map((proyecto) => ({
            queryKey: ['comentarios', { rondaId: ronda, proyecto }],
            queryFn: () => api.fetchComentarios(ronda, proyecto),
            staleTime: VIGENCIA,
            enabled: conComentarios,
        })),
    });
    const consultas = conComentarios ? [...fallas, ...comentarios] : fallas;
    return {
        porProyecto: claves.map((clave, i) => ({
            clave,
            fallas: fallas[i]?.data ?? [],
            comentarios: conComentarios ? comentarios[i]?.data ?? [] : [],
        })),
        isPending: consultas.some((c) => c.isPending),
        error: consultas.find((c) => c.error)?.error ?? null,
        refetch: () => Promise.all(consultas.map((c) => c.refetch())),
    };
};
