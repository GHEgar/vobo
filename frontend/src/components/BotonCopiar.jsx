import { useState } from 'react';
import { copiarTexto } from '@/utils/portapapeles';

export const BotonCopiar = ({ texto, etiqueta, descripcion }) => {
    const [copiado, setCopiado] = useState(false);
    return (
        <button
            type="button"
            aria-label={descripcion}
            onClick={async () => setCopiado(await copiarTexto(texto))}
            onBlur={() => setCopiado(false)}
            className="shrink-0 bg-transparent p-0 tipo-negrita text-xs text-primario underline underline-offset-4 hover:text-primario-hover"
        >
            {copiado ? 'Copiado' : etiqueta}
        </button>
    );
};
