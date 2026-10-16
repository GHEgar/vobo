import { useId } from 'react';
import { Plus } from 'tesela/react';

export const BotonMas = ({ etiqueta, ayuda, onClick }) => {
    const id = useId();
    return (
        <span className="group relative inline-flex">
            <button
                type="button"
                aria-label={etiqueta}
                aria-describedby={ayuda ? id : undefined}
                onClick={onClick}
                className="inline-flex h-[30px] w-[30px] items-center justify-center rounded-full border border-gris bg-transparent p-0 text-texto-tenue hover:border-primario hover:text-primario focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primario focus-visible:ring-offset-2"
            >
                <Plus size={18} />
            </button>
            {ayuda && (
                <span
                    id={id}
                    role="tooltip"
                    className="pointer-events-none absolute top-full right-0 z-20 mt-2 hidden w-max max-w-[min(280px,calc(100vw-32px))] rounded bg-neutro px-2 py-1 tipo-negrita text-[11px] text-white group-hover:block group-focus-within:block"
                >
                    {ayuda}
                </span>
            )}
        </span>
    );
};
