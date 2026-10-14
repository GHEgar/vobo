import { useId, useLayoutEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { IconoTooltip } from '@/components/Iconos';

const MARGEN = 8;

export const Tooltip = ({ text, label = 'Más información' }) => {
    const [abierto, setAbierto] = useState(false);
    const [coords, setCoords] = useState(null);
    const triggerRef = useRef(null);
    const panelRef = useRef(null);
    const id = useId();

    useLayoutEffect(() => {
        if (!abierto || !triggerRef.current || !panelRef.current) return;
        const t = triggerRef.current.getBoundingClientRect();
        const p = panelRef.current.getBoundingClientRect();
        const left = Math.max(MARGEN, Math.min(t.left + t.width / 2 - p.width / 2, window.innerWidth - p.width - MARGEN));
        const arriba = t.top - p.height - MARGEN;
        setCoords({ left, top: arriba >= MARGEN ? arriba : t.bottom + MARGEN });
    }, [abierto, text]);

    if (!text) return null;

    return (
        <span className="relative inline-flex align-middle">
            <button
                ref={triggerRef}
                type="button"
                aria-label={label}
                aria-describedby={abierto ? id : undefined}
                onMouseEnter={() => setAbierto(true)}
                onMouseLeave={() => setAbierto(false)}
                onFocus={() => setAbierto(true)}
                onBlur={() => setAbierto(false)}
                onClick={() => setAbierto((v) => !v)}
                className="inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-transparent p-0"
            >
                <IconoTooltip className="h-5 w-5" />
            </button>
            {abierto && createPortal(
                <div
                    ref={panelRef}
                    id={id}
                    role="tooltip"
                    style={{ top: coords?.top ?? 0, left: coords?.left ?? 0, visibility: coords ? 'visible' : 'hidden' }}
                    className="fixed z-[999] inline-flex w-[min(406px,calc(100vw-16px))] gap-4 rounded-[10px] bg-fondo px-6 py-4 text-start tipo-media text-xs/[21px] text-texto shadow-[0px_3px_12px_var(--color-sombra)]"
                >
                    <IconoTooltip className="h-5 w-5 shrink-0" />
                    <span>{text}</span>
                </div>,
                document.body,
            )}
        </span>
    );
};
