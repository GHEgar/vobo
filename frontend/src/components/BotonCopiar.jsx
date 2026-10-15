import { useState } from 'react';
import { Check, Copy } from 'tesela/react';
import { copiarTexto } from '@/utils/portapapeles';

export const BotonCopiar = ({ texto, etiqueta, descripcion }) => {
    const [copiado, setCopiado] = useState(false);
    return (
        <button
            type="button"
            aria-label={descripcion}
            onClick={async () => setCopiado(await copiarTexto(texto))}
            onBlur={() => setCopiado(false)}
            className="inline-flex shrink-0 items-center gap-1 bg-transparent p-0 tipo-negrita text-xs text-primario underline underline-offset-4 hover:text-primario-hover"
        >
            {copiado ? <Check size={14} stroke={2} /> : <Copy size={14} stroke={2} />}
            {copiado ? 'Copiado' : etiqueta}
        </button>
    );
};
