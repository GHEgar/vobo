import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import * as api from '@/services/validacion';

const MINUTO = 60 * 1000;

export const useAvisos = () => useQuery({
    queryKey: ['avisos', 'lista'],
    queryFn: api.fetchAvisos,
    staleTime: 15 * 1000,
});

export const useAvisosNoLeidos = () => useQuery({
    queryKey: ['avisos', 'no-leidos'],
    queryFn: api.fetchAvisosNoLeidos,
    refetchInterval: MINUTO,
    staleTime: 15 * 1000,
});

export const usePersonasAviso = () => useQuery({
    queryKey: ['avisos', 'personas'],
    queryFn: api.fetchPersonasAviso,
    staleTime: 5 * MINUTO,
});

const useMutacionAvisos = (mutationFn) => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn,
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ['avisos'] }),
    });
};

export const useCrearAviso = () => useMutacionAvisos(api.crearAviso);
export const useMarcarAvisoLeido = () => useMutacionAvisos(api.marcarAvisoLeido);
export const useMarcarAvisosLeidos = () => useMutacionAvisos(api.marcarAvisosLeidos);
