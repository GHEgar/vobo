import { useInfiniteQuery, useQuery } from '@tanstack/react-query';
import { fetchActividad, fetchResumenActividad } from '@/services/validacion';
import { useClaveProyecto } from '@/hooks/useProyecto';

const REFRESCO_MS = 30 * 1000;
const LIMITE = 40;

export const useResumenActividad = (activo = true) => {
    const proyecto = useClaveProyecto();
    return useQuery({
        queryKey: ['actividad', 'resumen', proyecto],
        queryFn: () => fetchResumenActividad(proyecto),
        refetchInterval: REFRESCO_MS,
        enabled: activo,
    });
};

export const useActividad = ({ usuario, tipos }) => {
    const proyecto = useClaveProyecto();
    const tipo = tipos.length ? [...tipos].sort().join(',') : '';
    return useInfiniteQuery({
        queryKey: ['actividad', 'eventos', proyecto, usuario, tipo],
        queryFn: ({ pageParam }) => fetchActividad({ proyecto, usuario, tipo, antes: pageParam, limite: LIMITE }),
        initialPageParam: null,
        getNextPageParam: (ultima) => ultima.siguiente,
        refetchInterval: REFRESCO_MS,
    });
};
