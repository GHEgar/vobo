import { useNavigate } from 'react-router';
import { useCombobox } from '@ghegar/muestrario';
import { buscar } from '@/services/validacion';
import { useRonda } from '@/hooks/useRonda';
import { useClaveProyecto } from '@/hooks/useProyecto';
import { Search } from 'tesela/react';
import { ListaResultados } from '@/components/buscador/ListaResultados';
import { useAtajoBuscar } from '@/components/buscador/useAtajoBuscar';
import { useRuta } from '@/hooks/useProyecto';

const MINIMO = 2;

const GRUPOS = {
    caso: 'Casos',
    paso: 'Pasos',
    seccion: 'Secciones',
    herramienta: 'Herramientas',
    procedimiento: 'Procedimientos',
};

const ETIQUETAS = {
    noResults: 'Sin resultados',
    loading: 'Buscando…',
    error: 'No se pudo buscar',
    clear: 'Limpiar',
    remove: 'Quitar',
    typeMore: (n) => `Escribe al menos ${n} caracteres`,
    results: (n) => `${n} ${n === 1 ? 'resultado' : 'resultados'}`,
};

export const Buscador = ({ className = '' }) => {
    const ruta = useRuta();
    const navigate = useNavigate();
    const { ronda } = useRonda();
    const proyecto = useClaveProyecto();
    const combo = useCombobox({
        getLabel: (r) => r.titulo,
        getKey: (r) => `${r.tipo}:${r.id}`,
        load: (q, signal) => buscar(q, ronda?.id, proyecto, signal),
        minChars: MINIMO,
        groupBy: (r) => GRUPOS[r.tipo],
        value: null,
        placement: 'bottom-end',
        onChange: (r) => {
            if (!r) return;
            navigate(ruta(r.ruta));
            queueMicrotask(() => combo.clear());
        },
        labels: ETIQUETAS,
    });
    const entrada = combo.getInputProps();
    const idEntrada = entrada.id;

    useAtajoBuscar(() => {
        const campo = document.getElementById(idEntrada);
        campo?.focus();
        campo?.select();
    });

    return (
        <div className={`relative h-[36px] ${className}`}>
            <div {...combo.getAnchorProps()} role="search" className="absolute top-0 right-0 w-full transition-[width] duration-200 ease-out focus-within:z-10 motion-reduce:transition-none @min-[60rem]:focus-within:w-[max(100%,260px)]">
                <Search size={16} className="pointer-events-none absolute top-1/2 left-3 -translate-y-1/2 text-primario" />
                <input
                    {...entrada}
                    type="search"
                    aria-label="Buscar casos, pasos y secciones"
                    aria-keyshortcuts="ñ Control+K Meta+K"
                    placeholder="Buscar (ñ)"
                    className="block h-[36px] w-full rounded-full border border-transparent bg-fondo pr-4 pl-9 tipo-media text-[13px] text-primario placeholder-texto-placeholder placeholder:tipo-regular hover:border-primario hover:bg-white focus:bg-white focus:outline-none focus:ring-1 focus:ring-primario [&::-webkit-search-cancel-button]:hidden"
                />
                {combo.open && <ListaResultados combo={combo} />}
                <span className="sr-only" {...combo.getStatusProps()}>{combo.statusText}</span>
            </div>
        </div>
    );
};
