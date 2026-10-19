import { useId, useState } from 'react';
import { ChevronRight } from 'tesela/react';

export const Dato = ({ termino, children }) => (
    <div className="min-w-0">
        <dt className="tipo-media text-[11px] text-texto-apagado">{termino}</dt>
        <dd className="wrap-anywhere tipo-media text-sm text-texto">{children || '—'}</dd>
    </div>
);

export const Detalles = ({ children, etiqueta = 'Detalles' }) => {
    const id = useId();
    const [abierto, setAbierto] = useState(false);
    return (
        <div className="mt-3">
            <button
                type="button"
                aria-expanded={abierto}
                aria-controls={id}
                onClick={() => setAbierto((actual) => !actual)}
                className="inline-flex min-h-[32px] items-center gap-1 rounded-full bg-transparent p-0 tipo-negrita text-xs text-primario hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primario"
            >
                <ChevronRight size={14} className={`shrink-0 transition-transform ${abierto ? 'rotate-90' : ''}`} />
                {etiqueta}
            </button>
            <dl id={id} hidden={!abierto} className="mt-2 grid grid-cols-1 gap-3 rounded-xl bg-fondo p-4 sm:grid-cols-2 lg:grid-cols-3">
                {children}
            </dl>
        </div>
    );
};
