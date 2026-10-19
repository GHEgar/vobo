import { forwardRef, useCallback, useEffect, useId, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { usePosition } from '@ghegar/plomada/react';

const BASE = 'relative inline-flex h-[34px] w-[34px] shrink-0 items-center justify-center rounded-full border p-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primario focus-visible:ring-offset-2';
const TONOS = {
    neutro: 'border-gris bg-transparent text-texto-tenue hover:border-primario hover:text-primario',
    activo: 'border-primario bg-primario-claro text-primario',
    marca: 'border-transparent bg-primario-claro text-primario hover:border-primario',
    exito: 'border-transparent bg-pasa-fondo text-pasa hover:border-pasa',
    error: 'border-transparent bg-falla-fondo text-falla hover:border-falla',
    aviso: 'border-transparent bg-pendiente-fondo text-pendiente hover:border-pendiente',
};

export const BotonIcono = forwardRef(({ etiqueta, icono: Icono, tono = 'neutro', marca = false, className = '', ...rest }, ref) => (
    <button ref={ref} type="button" aria-label={etiqueta} title={etiqueta} className={`${BASE} ${TONOS[tono]} ${className}`} {...rest}>
        <Icono size={18} className="shrink-0" />
        {marca && <span aria-hidden="true" className="absolute -top-0.5 -right-0.5 h-2.5 w-2.5 rounded-full border-2 border-white bg-falla" />}
    </button>
));

BotonIcono.displayName = 'BotonIcono';

export const BotonEmergente = ({ etiqueta, titulo, icono, tono, marca, children }) => {
    const [abierto, setAbierto] = useState(false);
    const id = useId();
    const boton = useRef(null);
    const panel = useRef(null);
    const posicion = usePosition({ open: abierto, placement: 'bottom-end', offset: 8 });
    const { setReference, setFloating, floatingStyles } = posicion;

    useEffect(() => {
        if (!abierto) return undefined;
        const fuera = (e) => {
            if (e.target.closest?.('[data-emergente-anidado]')) return;
            if (!panel.current?.contains(e.target) && !boton.current?.contains(e.target)) setAbierto(false);
        };
        const tecla = (e) => {
            if (e.key !== 'Escape') return;
            if (e.target.getAttribute?.('role') === 'combobox' && e.target.getAttribute('aria-expanded') === 'true') return;
            setAbierto(false);
            boton.current?.focus();
        };
        document.addEventListener('pointerdown', fuera);
        document.addEventListener('keydown', tecla);
        const marco = requestAnimationFrame(() => panel.current?.querySelector('select, input, button')?.focus());
        return () => {
            document.removeEventListener('pointerdown', fuera);
            document.removeEventListener('keydown', tecla);
            cancelAnimationFrame(marco);
        };
    }, [abierto]);

    const unir = useCallback((el) => {
        boton.current = el;
        setReference(el);
    }, [setReference]);
    const unirPanel = useCallback((el) => {
        panel.current = el;
        setFloating(el);
    }, [setFloating]);

    return (
        <>
            <BotonIcono
                ref={unir}
                etiqueta={etiqueta}
                icono={icono}
                tono={tono}
                marca={marca}
                aria-expanded={abierto}
                aria-controls={id}
                aria-haspopup="dialog"
                onClick={() => setAbierto((actual) => !actual)}
            />
            {abierto && createPortal(
                <div
                    ref={unirPanel}
                    style={floatingStyles}
                    id={id}
                    role="dialog"
                    aria-label={titulo}
                    className="z-50 w-[min(340px,calc(100vw-32px))] rounded-2xl bg-white p-4 shadow-[0px_3px_24px_var(--color-sombra-menu)]"
                >
                    <p className="tipo-negrita text-sm text-texto">{titulo}</p>
                    <div className="mt-3 flex flex-col gap-4">{children}</div>
                </div>,
                document.body,
            )}
        </>
    );
};
