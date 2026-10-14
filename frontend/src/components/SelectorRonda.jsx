import { useRonda } from '@/hooks/useRonda';
import { SelectField } from '@/components/Field';
import { Tooltip } from '@/components/Tooltip';

export const SelectorRonda = () => {
    const { rondas, ronda, elegirRonda } = useRonda();
    if (!rondas.length) return null;
    return (
        <div className="relative w-[200px] md:w-[240px]">
            <span className="absolute top-1/2 left-2 z-10 -translate-y-1/2">
                <Tooltip text="Cada ronda es una pasada completa sobre el entorno de prueba recién restaurado. Lo que marcas se guarda en la ronda elegida." />
            </span>
            <SelectField
                id="ronda"
                aria-label="Ronda"
                value={ronda?.id ?? ''}
                onChange={(e) => elegirRonda(Number(e.target.value))}
                options={rondas.map((r) => ({ valor: r.id, texto: `${r.nombre}${r.abierta ? '' : ' (cerrada)'}` }))}
                claseControl="h-[38px]! appearance-none rounded-full! py-0! pl-10 pr-10"
            />
            <svg aria-hidden="true" viewBox="0 0 12 8" className="pointer-events-none absolute top-1/2 right-4 h-2 w-3 -translate-y-1/2 text-primario">
                <path d="M1 1l5 5 5-5" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
        </div>
    );
};
