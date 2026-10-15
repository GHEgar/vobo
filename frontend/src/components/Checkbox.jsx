import { useEffect, useRef } from 'react';
import { Check, Minus } from 'tesela/react';

const TONOS = {
    marca: { caja: 'checked:border-primario checked:bg-primario indeterminate:border-primario hover:border-primario', marca: 'text-primario' },
    naranja: { caja: 'checked:border-aviso checked:bg-aviso indeterminate:border-aviso hover:border-aviso', marca: 'text-aviso' },
};

export const Checkbox = ({ id, checked, onChange, disabled, indeterminado = false, tono = 'marca', etiqueta, describe, children }) => {
    const ref = useRef(null);

    useEffect(() => {
        if (ref.current) ref.current.indeterminate = indeterminado;
    }, [indeterminado, checked]);

    return (
        <div className="flex items-start gap-3">
            <span className="relative mt-0.5 flex h-5 w-5 shrink-0">
                <input
                    ref={ref}
                    type="checkbox"
                    id={id}
                    checked={checked}
                    disabled={disabled}
                    aria-checked={indeterminado ? 'mixed' : checked}
                    aria-label={etiqueta}
                    aria-describedby={describe}
                    onChange={(e) => onChange(e.target.checked)}
                    className={`h-5 w-5 cursor-pointer appearance-none rounded-sm border border-borde-control indeterminate:bg-white hover:shadow-lg hover:shadow-sombra-foco disabled:cursor-not-allowed ${TONOS[tono].caja}`}
                />
                {indeterminado
                    ? <Minus size={14} stroke={2.5} className={`pointer-events-none absolute inset-0 m-auto ${TONOS[tono].marca}`} />
                    : checked && <Check size={14} stroke={2.5} className="pointer-events-none absolute inset-0 m-auto text-white" />}
            </span>
            {children && (
                <label htmlFor={id} className="cursor-pointer tipo-media text-sm/6 text-texto">
                    {children}
                </label>
            )}
        </div>
    );
};
