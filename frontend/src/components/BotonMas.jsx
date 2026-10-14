import { useId } from 'react';

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
                <svg aria-hidden="true" viewBox="0 0 16 16" className="h-4 w-4">
                    <path d="M8 2.5v11M2.5 8h11" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                </svg>
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
