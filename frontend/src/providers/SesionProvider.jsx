import { useMemo } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { SesionContext } from '@/contexts/SesionContext';
import { fijarCsrf } from '@/services/api';
import { fetchSesion, salir as salirApi } from '@/services/validacion';
import { limpiarMarcasEntrada, marcarSesionCerrada } from '@/utils/entrada';

const leerSesion = async () => {
    try {
        const sesion = await fetchSesion();
        fijarCsrf(sesion.csrf_token);
        limpiarMarcasEntrada();
        return sesion;
    } catch (error) {
        if (error.estado === 401) return null;
        throw error;
    }
};

export const SesionProvider = ({ children }) => {
    const queryClient = useQueryClient();
    const { data, isPending, error, refetch } = useQuery({
        queryKey: ['sesion'],
        queryFn: leerSesion,
        staleTime: 5 * 60 * 1000,
        retry: false,
    });

    const valor = useMemo(() => {
        const usuario = data?.usuario ?? null;
        const permisos = new Set(usuario?.permisos ?? []);
        const paginas = new Set(usuario?.paginas ?? []);
        return {
            usuario,
            cargando: isPending,
            error,
            reintentar: refetch,
            puede: (permiso) => permisos.has(permiso),
            ve: (pagina) => paginas.has(pagina),
            refrescar: () => queryClient.invalidateQueries({ queryKey: ['sesion'] }),
            salir: async () => {
                await salirApi().catch(() => null);
                fijarCsrf('');
                queryClient.clear();
                marcarSesionCerrada();
                window.location.assign('/');
            },
        };
    }, [data, isPending, error, refetch, queryClient]);

    return <SesionContext value={valor}>{children}</SesionContext>;
};
