import { useRef } from 'react';
import { AgregarFantasma } from '@/components/edicion/Editable';
import { FilaSeccion } from '@/components/inicio/FilaSeccion';
import { SelectorModo } from '@/components/inicio/SelectorModo';

export const PestanasSistemas = ({ id, grupos, estados, elegido, onElegir, modos = {}, onCambiarModo, destacado, edicion = null }) => {
    const pestanasRef = useRef([]);
    const indice = Math.max(0, grupos.findIndex((g) => g.clave === elegido));
    const activo = grupos[indice];

    const mover = (e) => {
        const pasos = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1, Home: -indice, End: grupos.length - 1 - indice };
        if (!(e.key in pasos)) return;
        e.preventDefault();
        const siguiente = (indice + pasos[e.key] + grupos.length) % grupos.length;
        onElegir(grupos[siguiente].clave);
        pestanasRef.current[siguiente]?.focus();
    };

    if (!activo) return null;

    const funcionales = activo.secciones.filter((s) => s.audiencia !== 'tecnica');
    const tecnicas = activo.secciones.filter((s) => s.audiencia === 'tecnica');
    const ambos = funcionales.length > 0 && tecnicas.length > 0;
    const modo = ambos ? (modos[activo.clave] ?? 'funcional') : (funcionales.length ? 'funcional' : 'tecnica');
    const lista = modo === 'tecnica' ? tecnicas : funcionales;

    return (
        <section id={id} className="scroll-mt-40 rounded-2xl bg-white sm:scroll-mt-36 shadow-[0px_3px_12px_var(--color-sombra-tenue)]">
            <h2 className="px-4 pt-5 tipo-negrita text-lg text-texto md:px-6">
                Secciones <span className="tipo-media text-sm text-texto-apagado">({grupos.reduce((n, g) => n + g.secciones.length, 0)})</span>
            </h2>
            <div className="md:grid md:grid-cols-[240px_minmax(0,1fr)] md:gap-4 md:px-6 md:pb-5">
                <div
                    role="tablist"
                    aria-label="Sistemas"
                    aria-orientation="vertical"
                    className="flex gap-2 overflow-x-auto px-4 pt-4 pb-3 [scrollbar-width:none] [mask-image:linear-gradient(to_right,transparent,black_16px,black_calc(100%-16px),transparent)] md:max-h-[60dvh] md:flex-col md:overflow-x-visible md:overflow-y-auto md:px-0 md:py-4 md:[mask-image:linear-gradient(to_bottom,transparent,black_16px,black_calc(100%-16px),transparent)]"
                >
                    {grupos.map((g, i) => {
                        const seleccionado = i === indice;
                        return (
                            <button
                                key={g.clave}
                                ref={(el) => { pestanasRef.current[i] = el; }}
                                type="button"
                                role="tab"
                                id={`${id}-tab-${g.clave}`}
                                aria-selected={seleccionado}
                                aria-controls={`${id}-panel`}
                                tabIndex={seleccionado ? 0 : -1}
                                onClick={() => onElegir(g.clave)}
                                onKeyDown={mover}
                                className={`inline-flex h-auto min-h-[36px] shrink-0 items-center gap-2 rounded-full px-4 py-1 text-left tipo-negrita text-xs md:w-full md:justify-between ${seleccionado ? 'bg-primario text-white' : 'bg-fondo text-texto-tenue hover:bg-primario-claro md:bg-transparent md:hover:bg-primario-claro'}`}
                            >
                                {g.nombre}
                                <span className={`tipo-media ${seleccionado ? 'text-primario-claro' : 'text-texto-apagado'}`}>{g.hechos}/{g.total}</span>
                            </button>
                        );
                    })}
                </div>
                <div role="tabpanel" id={`${id}-panel`} aria-labelledby={`${id}-tab-${activo.clave}`} tabIndex={0} className="px-4 pb-5 md:px-0 md:pt-4 md:pb-0">
                    {ambos && (
                        <div className="mb-3 flex flex-wrap items-center gap-2">
                            <SelectorModo
                                modo={modo}
                                onCambiar={(valor) => onCambiarModo(activo.clave, valor)}
                                conteos={{ funcional: funcionales.length, tecnica: tecnicas.length }}
                            />
                        </div>
                    )}
                    <ul className="flex flex-col gap-3">
                        {lista.map((s) => (
                            <FilaSeccion
                                key={`${activo.clave}-${modo}-${s.id}`}
                                seccion={s}
                                estados={estados}
                                abiertoInicial={lista.length === 1 || s.casos.some((c) => c.id === destacado)}
                                destacado={destacado}
                                acciones={edicion?.acciones(s, lista)}
                            />
                        ))}
                        {edicion && (
                            <li>
                                <AgregarFantasma texto="Agregar sección" onClick={() => edicion.onNueva(activo.clave, modo)} />
                            </li>
                        )}
                    </ul>
                </div>
            </div>
        </section>
    );
};
