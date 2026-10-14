import { useId } from 'react';

export const Plegable = ({ titulo, resumen, abierto, onAlternar, children }) => {
    const id = useId();
    return (
        <section className="rounded-2xl bg-white shadow-[0px_3px_12px_var(--color-sombra-tenue)]">
            <button
                type="button"
                onClick={onAlternar}
                aria-expanded={abierto}
                aria-controls={id}
                className="flex w-full items-center justify-between gap-3 rounded-2xl bg-transparent px-5 py-4 text-left hover:bg-primario-suave md:px-7"
            >
                <span className="tipo-negrita text-sm text-texto">
                    {titulo}
                    {resumen && <span className="tipo-media text-texto-tenue"> · {resumen}</span>}
                </span>
                <span aria-hidden="true" className={`tipo-negrita text-primario transition-transform ${abierto ? 'rotate-90' : ''}`}>▸</span>
            </button>
            {abierto && <div id={id} className="px-5 pb-5 md:px-7 md:pb-7">{children}</div>}
        </section>
    );
};
