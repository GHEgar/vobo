import { useMemo } from 'react';
import { useRondas } from '@/hooks/useValidacion';
import { useLocalStorageState } from '@/hooks/useLocalStorageState';
import { RondaContext } from '@/contexts/RondaContext';

export const RondaProvider = ({ children }) => {
    const { data: rondas = [], isPending, error } = useRondas();
    const [elegida, setElegida] = useLocalStorageState('validacion.ronda', null);

    const valor = useMemo(() => {
        const ronda = rondas.find((r) => r.id === elegida)
            ?? rondas.find((r) => r.abierta)
            ?? rondas[0]
            ?? null;
        return { rondas, ronda, cargando: isPending, error, elegirRonda: setElegida };
    }, [rondas, elegida, isPending, error, setElegida]);

    return <RondaContext value={valor}>{children}</RondaContext>;
};
