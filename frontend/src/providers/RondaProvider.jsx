import { useMemo } from 'react';
import { useRondas } from '@/hooks/useValidacion';
import { useLocalStorageState } from '@/hooks/useLocalStorageState';
import { useProyecto } from '@/hooks/useProyecto';
import { RondaContext } from '@/contexts/RondaContext';

const Elegida = ({ clave, children }) => {
    const { data: rondas = [], isPending, error } = useRondas();
    const [elegida, setElegida] = useLocalStorageState(clave, null);

    const valor = useMemo(() => {
        const ronda = rondas.find((r) => r.id === elegida)
            ?? rondas.find((r) => r.abierta)
            ?? rondas[0]
            ?? null;
        return { rondas, ronda, cargando: isPending, error, elegirRonda: setElegida };
    }, [rondas, elegida, isPending, error, setElegida]);

    return <RondaContext value={valor}>{children}</RondaContext>;
};

export const RondaProvider = ({ children }) => {
    const { proyecto } = useProyecto();
    const clave = proyecto && !proyecto.por_omision ? `validacion.ronda.${proyecto.clave}` : 'validacion.ronda';
    return <Elegida key={clave} clave={clave}>{children}</Elegida>;
};
