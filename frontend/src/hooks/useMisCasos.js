import { useMemo } from 'react';
import { useContenido, useMisCasos } from '@/hooks/useValidacion';
import { useRonda } from '@/hooks/useRonda';
import { indexarContenido, resumirProgreso } from '@/utils/progreso';

export const useProgreso = (audiencia = null) => {
    const { ronda } = useRonda();
    const contenido = useContenido();
    const mis = useMisCasos(ronda?.id);

    const datos = useMemo(() => {
        if (!contenido.data) return null;
        const indice = indexarContenido(contenido.data);
        return { indice, ...resumirProgreso(indice, mis.data, audiencia) };
    }, [contenido.data, mis.data, audiencia]);

    return {
        ronda,
        datos,
        cargando: contenido.isPending || (Boolean(ronda) && mis.isPending),
        error: contenido.error || mis.error,
        reintentar: () => {
            contenido.refetch();
            mis.refetch();
        },
    };
};
