import { useEffect, useId, useRef } from 'react';
import { createPortal } from 'react-dom';
import { IconoCerrar } from '@/components/Iconos';

const ENFOCABLES = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

export const Modal = ({ abierto, titulo, onCerrar, children, ancho = 'max-w-[812px]' }) => {
    const tituloId = useId();
    const dialogoRef = useRef(null);

    useEffect(() => {
        if (!abierto) return undefined;
        const anterior = document.activeElement;
        const dialogo = dialogoRef.current;
        dialogo?.querySelector(ENFOCABLES)?.focus();
        const teclas = (e) => {
            if (e.key === 'Escape') {
                e.preventDefault();
                onCerrar();
                return;
            }
            const enfocables = dialogo?.querySelectorAll(ENFOCABLES);
            if (e.key !== 'Tab' || !enfocables?.length) return;
            const primero = enfocables[0];
            const ultimo = enfocables[enfocables.length - 1];
            if (e.shiftKey && document.activeElement === primero) {
                e.preventDefault();
                ultimo.focus();
            } else if (!e.shiftKey && document.activeElement === ultimo) {
                e.preventDefault();
                primero.focus();
            }
        };
        document.addEventListener('keydown', teclas);
        return () => {
            document.removeEventListener('keydown', teclas);
            anterior?.focus?.();
        };
    }, [abierto, onCerrar]);

    if (!abierto) return null;

    return createPortal(
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={(e) => e.target === e.currentTarget && onCerrar()} role="presentation">
            <div
                ref={dialogoRef}
                role="dialog"
                aria-modal="true"
                aria-labelledby={tituloId}
                className={`flex max-h-[92dvh] w-full ${ancho} flex-col gap-4 overflow-auto rounded-2xl bg-white p-5 shadow-lg md:p-8`}
            >
                <div className="flex items-start justify-between gap-4">
                    <h2 id={tituloId} className="tipo-negrita text-[18px] text-texto md:text-[21px]">{titulo}</h2>
                    <button type="button" onClick={onCerrar} aria-label="Cerrar" className="shrink-0 rounded-full bg-transparent p-0 hover:shadow-[0px_3px_12px_var(--color-sombra)]">
                        <IconoCerrar className="h-6 w-6" />
                    </button>
                </div>
                {children}
            </div>
        </div>,
        document.body,
    );
};
