import { createPortal } from 'react-dom';
import { Resaltado } from '@/components/buscador/Resaltado';
import { Search } from 'tesela/react';

const ALTO_MAXIMO = 480;

const Opcion = ({ combo, resultado, indice }) => (
    <div
        {...combo.getOptionProps(resultado, indice)}
        className="cursor-pointer rounded-xl px-3 py-2 data-[active]:bg-primario-claro"
    >
        <p className="truncate tipo-negrita text-sm text-texto">
            <Resaltado texto={resultado.titulo} consulta={combo.inputValue} />
        </p>
        {resultado.contexto && (
            <p className="mt-0.5 line-clamp-2 tipo-media text-xs/5 text-texto-apagado">
                <Resaltado texto={resultado.contexto} consulta={combo.inputValue} />
            </p>
        )}
    </div>
);

export const ListaResultados = ({ combo }) => {
    const props = combo.getListboxProps();
    const alto = Math.min(combo.position?.availableHeight ?? ALTO_MAXIMO, ALTO_MAXIMO);
    const vacio = !combo.items.length;

    return createPortal(
        <div
            {...props}
            style={{ ...props.style, maxHeight: alto }}
            className="z-50 min-w-[min(440px,calc(100vw-16px))] overflow-y-auto rounded-2xl bg-white p-2 shadow-[0px_3px_24px_var(--color-sombra-menu)]"
        >
            {vacio && combo.statusText && (
                <p aria-hidden="true" className="flex items-center gap-2 px-3 py-2 tipo-media text-sm text-texto-apagado"><Search size={16} className="shrink-0" />{combo.statusText}</p>
            )}
            {combo.groups?.map((grupo) => (
                <div key={grupo.label} {...combo.getGroupProps(grupo)} className="py-1">
                    <div {...combo.getGroupLabelProps(grupo)} className="px-3 pt-1 pb-1 tipo-negrita text-[11px] tracking-wide text-texto-apagado uppercase">
                        {grupo.label}
                    </div>
                    {grupo.options.map(({ item, index }) => (
                        <Opcion key={`${item.tipo}:${item.id}`} combo={combo} resultado={item} indice={index} />
                    ))}
                </div>
            ))}
        </div>,
        document.body,
    );
};
