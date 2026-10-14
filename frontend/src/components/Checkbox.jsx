import { useEffect, useRef } from 'react';

const TONOS = {
    marca: 'checked:border-primario checked:bg-primario indeterminate:border-primario indeterminate:before:text-primario hover:border-primario',
    naranja: 'checked:border-aviso checked:bg-aviso indeterminate:border-aviso indeterminate:before:text-aviso hover:border-aviso',
};

export const Checkbox = ({ id, checked, onChange, disabled, indeterminado = false, tono = 'marca', etiqueta, describe, children }) => {
    const ref = useRef(null);

    useEffect(() => {
        if (ref.current) ref.current.indeterminate = indeterminado;
    }, [indeterminado, checked]);

    return (
        <div className="flex items-start gap-3">
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
                className={`mt-0.5 h-5 w-5 shrink-0 cursor-pointer appearance-none rounded-sm border border-borde-control checked:before:flex checked:before:h-full checked:before:items-center checked:before:justify-center checked:before:text-[14px] checked:before:text-white checked:before:content-['✔'] indeterminate:bg-white indeterminate:before:flex indeterminate:before:h-full indeterminate:before:items-center indeterminate:before:justify-center indeterminate:before:tipo-negrita indeterminate:before:text-[14px] indeterminate:before:content-['—'] hover:shadow-lg hover:shadow-sombra-foco disabled:cursor-not-allowed ${TONOS[tono]}`}
            />
            {children && (
                <label htmlFor={id} className="cursor-pointer tipo-media text-sm/6 text-texto">
                    {children}
                </label>
            )}
        </div>
    );
};
