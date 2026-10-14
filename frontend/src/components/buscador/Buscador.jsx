import { useState } from 'react';
import { flushSync } from 'react-dom';
import { useNavigate } from 'react-router';
import { useCombobox } from '@ghegar/muestrario';
import { buscar } from '@/services/validacion';
import { useRonda } from '@/hooks/useRonda';
import { IconoBuscar } from '@/components/Iconos';
import { ListaResultados } from '@/components/buscador/ListaResultados';
import { useAtajoBuscar } from '@/components/buscador/useAtajoBuscar';

const MINIMO = 2;

const CAMPO_DESPLEGADO = 'absolute inset-x-3 top-full z-40 mt-2 lg:left-auto lg:w-[420px]';

const CAMPO_EN_LINEA = 'md:max-lg:relative md:max-lg:inset-auto md:max-lg:mt-0 md:max-lg:block md:max-lg:w-[220px] xl:relative xl:inset-auto xl:mt-0 xl:block xl:w-[170px]';

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

export const Buscador = () => {
    const navigate = useNavigate();
    const { ronda } = useRonda();
    const [desplegado, setDesplegado] = useState(false);
    const combo = useCombobox({
        getLabel: (r) => r.titulo,
        getKey: (r) => `${r.tipo}:${r.id}`,
        load: (q, signal) => buscar(q, ronda?.id, signal),
        minChars: MINIMO,
        groupBy: (r) => GRUPOS[r.tipo],
        value: null,
        onChange: (r) => {
            if (!r) return;
            navigate(r.ruta);
            queueMicrotask(() => combo.clear());
        },
        labels: ETIQUETAS,
    });
    const entrada = combo.getInputProps();
    const idEntrada = entrada.id;

    const enfocar = () => {
        flushSync(() => setDesplegado(true));
        const campo = document.getElementById(idEntrada);
        campo?.focus();
        campo?.select();
    };
    useAtajoBuscar(enfocar);

    return (
        <>
            <button
                type="button"
                aria-label="Buscar"
                aria-keyshortcuts="/ Control+K Meta+K"
                onClick={enfocar}
                className={`${desplegado ? 'hidden' : 'flex'} h-[36px] w-[36px] items-center justify-center rounded-full bg-primario-claro text-primario hover:ring-2 hover:ring-primario-anillo focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primario md:max-lg:hidden xl:hidden`}
            >
                <IconoBuscar className="h-5 w-5" />
            </button>
            <div
                {...combo.getAnchorProps()}
                className={`${desplegado ? CAMPO_DESPLEGADO : 'relative hidden'} ${CAMPO_EN_LINEA}`}
            >
                <IconoBuscar className="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-primario" />
                <input
                    {...entrada}
                    type="search"
                    aria-label="Buscar casos, pasos y secciones"
                    aria-keyshortcuts="/ Control+K Meta+K"
                    placeholder="Buscar ( / )"
                    onBlur={(e) => {
                        entrada.onBlur(e);
                        setDesplegado(false);
                    }}
                    className="block h-[36px] w-full rounded-full border border-transparent bg-fondo pr-4 pl-9 tipo-media text-[13px] text-primario shadow-[0px_3px_12px_var(--color-sombra-suave)] placeholder-texto-placeholder placeholder:tipo-regular hover:border-primario hover:bg-white focus:bg-white focus:outline-none focus:ring-1 focus:ring-primario md:shadow-none [&::-webkit-search-cancel-button]:hidden"
                />
            </div>
            {combo.open && <ListaResultados combo={combo} />}
            <span className="sr-only" {...combo.getStatusProps()}>{combo.statusText}</span>
        </>
    );
};
