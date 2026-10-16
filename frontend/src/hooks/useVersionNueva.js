import { useQuery } from '@tanstack/react-query';
import { fetchVersion } from '@/services/validacion';
import { hayVersionNueva } from '@/utils/version';

const VERSION_CONSTRUIDA = import.meta.env.VITE_APP_VERSION ?? '';
const CINCO_MINUTOS = 5 * 60 * 1000;

export const useVersionNueva = () => {
    const { data } = useQuery({
        queryKey: ['version'],
        queryFn: fetchVersion,
        enabled: Boolean(VERSION_CONSTRUIDA),
        staleTime: 0,
        refetchInterval: CINCO_MINUTOS,
        refetchOnWindowFocus: 'always',
        retry: false,
    });
    return hayVersionNueva(VERSION_CONSTRUIDA, data?.version);
};
