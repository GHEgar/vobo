import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { useMenu } from '@ghegar/abanico';
import { Check, ChevronDown } from 'tesela/react';

const BOTON = 'flex h-[38px] w-full cursor-pointer items-center gap-2 rounded-full border border-transparent bg-fondo pr-10 text-left tipo-media text-[13px] text-primario hover:border-primario hover:bg-white hover:shadow-[0px_2px_24px_var(--color-sombra-campo)] focus:outline-none focus-visible:bg-white focus-visible:ring-1 focus-visible:ring-primario aria-expanded:bg-white aria-expanded:ring-1 aria-expanded:ring-primario';

export const Desplegable = ({ opciones, value, onChange, 'aria-label': etiqueta, prefijo, className = '' }) => {
    const [ancho, setAncho] = useState(0);
    const elegida = opciones.find((o) => o.valor === value) ?? null;
    const menu = useMenu({
        count: opciones.length,
        getLabel: (i) => opciones[i]?.texto ?? '',
        onSelect: (i) => {
            onChange(opciones[i].valor);
            menu.close();
        },
    });
    const boton = menu.getButtonProps();
    const lista = menu.getMenuProps();
    const colocado = menu.open && menu.position !== null;

    useEffect(() => {
        if (!colocado) return undefined;
        const marco = requestAnimationFrame(() => {
            document.getElementById(lista.id)?.querySelector('[aria-checked="true"]')?.focus();
        });
        return () => cancelAnimationFrame(marco);
    }, [colocado, lista.id]);
    const medir = (e) => setAncho(e.currentTarget.getBoundingClientRect().width);

    return (
        <div className={`relative ${className}`}>
            {prefijo && <span className="absolute top-1/2 left-2 z-10 -translate-y-1/2">{prefijo}</span>}
            <button
                {...boton}
                onClick={(e) => {
                    medir(e);
                    boton.onClick();
                }}
                onKeyDown={(e) => {
                    medir(e);
                    boton.onKeyDown(e);
                }}
                className={`${BOTON} ${prefijo ? 'pl-10' : 'pl-4'}`}
            >
                <span className="sr-only">{etiqueta}: </span>
                <span className="min-w-0 truncate">{elegida?.texto ?? ''}</span>
                {elegida?.extra && <span className="flex shrink-0 *:min-h-[22px] *:px-2.5 *:py-0">{elegida.extra}</span>}
            </button>
            <ChevronDown size={16} stroke={2} className="pointer-events-none absolute top-1/2 right-3.5 -translate-y-1/2 text-primario" />
            {menu.open && createPortal(
                <div
                    {...lista}
                    style={{ ...lista.style, minWidth: ancho || undefined }}
                    className="z-50 max-h-[60dvh] overflow-y-auto rounded-2xl bg-white p-2 shadow-[0px_3px_24px_var(--color-sombra-menu)] focus:outline-none"
                >
                    {opciones.map((opcion, i) => {
                        const marcada = opcion.valor === value;
                        return (
                            <div
                                key={opcion.valor}
                                {...menu.getItemProps(i, { type: 'radio', checked: marcada })}
                                className={`flex cursor-pointer items-center gap-2 rounded-xl py-2 pr-3 pl-2 text-sm outline-none data-[active]:bg-primario-claro ${marcada ? 'tipo-negrita text-primario' : 'tipo-media text-texto-tenue'}`}
                            >
                                <span className="flex w-4 shrink-0 justify-center">
                                    {marcada && <Check size={16} stroke={2} />}
                                </span>
                                <span className="min-w-0 flex-1 truncate">{opcion.texto}</span>
                                {opcion.extra}
                            </div>
                        );
                    })}
                </div>,
                document.body,
            )}
        </div>
    );
};
