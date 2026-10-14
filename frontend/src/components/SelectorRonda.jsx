import { useRonda } from '@/hooks/useRonda';
import { Chip } from '@/components/Chip';
import { Desplegable } from '@/components/Desplegable';
import { Tooltip } from '@/components/Tooltip';

export const SelectorRonda = () => {
    const { rondas, ronda, elegirRonda } = useRonda();
    if (!rondas.length) return null;
    return (
        <Desplegable
            aria-label="Ronda"
            value={ronda?.id ?? null}
            onChange={elegirRonda}
            opciones={rondas.map((r) => ({
                valor: r.id,
                texto: r.nombre,
                extra: r.abierta ? null : <Chip>Cerrada</Chip>,
            }))}
            prefijo={<Tooltip text="Cada ronda es una pasada completa sobre el entorno de prueba recién restaurado. Lo que marcas se guarda en la ronda elegida." />}
            className="w-[200px] md:w-[240px]"
        />
    );
};
