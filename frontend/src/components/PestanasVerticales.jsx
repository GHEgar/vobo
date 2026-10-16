import { useRef } from 'react';

export const PestanasVerticales = ({ id, titulo, etiqueta = 'Sistemas', pestanas, elegida, onElegir, children }) => {
    const refs = useRef([]);
    const indice = Math.max(0, pestanas.findIndex((p) => p.clave === elegida));
    const activa = pestanas[indice];

    const mover = (e) => {
        const pasos = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1, Home: -indice, End: pestanas.length - 1 - indice };
        if (!(e.key in pasos)) return;
        e.preventDefault();
        const siguiente = (indice + pasos[e.key] + pestanas.length) % pestanas.length;
        onElegir(pestanas[siguiente].clave);
        refs.current[siguiente]?.focus();
    };

    if (!activa) return null;

    return (
        <section id={id} className="rounded-2xl bg-white shadow-[0px_3px_12px_var(--color-sombra-tenue)]">
            {titulo && <h2 className="px-4 pt-5 tipo-negrita text-lg text-texto md:px-6">{titulo}</h2>}
            <div className="md:grid md:grid-cols-[240px_minmax(0,1fr)] md:gap-4 md:px-6 md:pb-5">
                <div
                    role="tablist"
                    aria-label={etiqueta}
                    aria-orientation="vertical"
                    className="flex gap-2 overflow-x-auto px-4 pt-4 pb-3 [scrollbar-width:none] [mask-image:linear-gradient(to_right,transparent,black_16px,black_calc(100%-16px),transparent)] md:max-h-[70dvh] md:flex-col md:overflow-x-visible md:overflow-y-auto md:px-0 md:py-4 md:[mask-image:linear-gradient(to_bottom,transparent,black_16px,black_calc(100%-16px),transparent)]"
                >
                    {pestanas.map((p, i) => {
                        const seleccionada = i === indice;
                        return (
                            <button
                                key={p.clave}
                                ref={(el) => { refs.current[i] = el; }}
                                type="button"
                                role="tab"
                                id={`${id}-tab-${p.clave}`}
                                aria-selected={seleccionada}
                                aria-controls={`${id}-panel`}
                                tabIndex={seleccionada ? 0 : -1}
                                onClick={() => onElegir(p.clave)}
                                onKeyDown={mover}
                                className={`inline-flex min-h-[36px] shrink-0 items-center gap-2 rounded-full px-4 py-1 text-left tipo-negrita text-xs md:w-full md:justify-between ${seleccionada ? 'bg-primario text-white' : 'bg-fondo text-texto-tenue hover:bg-primario-claro md:bg-transparent'}`}
                            >
                                <span className="inline-flex items-center gap-2">
                                    {p.icono && <p.icono size={16} className="shrink-0" />}
                                    {p.nombre}
                                </span>
                                {p.contador && <span className={`tipo-media ${seleccionada ? 'text-primario-claro' : 'text-texto-apagado'}`}>{p.contador}</span>}
                            </button>
                        );
                    })}
                </div>
                <div role="tabpanel" id={`${id}-panel`} aria-labelledby={`${id}-tab-${activa.clave}`} tabIndex={0} className="px-4 pb-5 md:px-0 md:pt-4 md:pb-0">
                    {children(activa)}
                </div>
            </div>
        </section>
    );
};
