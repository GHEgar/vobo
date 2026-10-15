import { Link } from 'react-router';
import { ChevronRight } from 'tesela/react';

const BASE = 'inline-flex h-[38px] items-center gap-1 rounded-full px-5 tipo-negrita text-xs';

export const Continuar = ({ objetivo }) => {
    if (!objetivo) {
        return <span className={`${BASE} cursor-default bg-pasa-fondo text-pasa`}>Terminaste</span>;
    }
    const { caso, paso } = objetivo;
    return (
        <Link
            to={`/caso/${encodeURIComponent(caso.id)}`}
            title={`${caso.titulo} · Paso ${paso + 1} de ${caso.pasos.length}`}
            aria-label={`Continuar con ${caso.id}: ${caso.titulo}, paso ${paso + 1} de ${caso.pasos.length}`}
            className={`${BASE} bg-aviso text-white hover:shadow-[0px_8px_16px_var(--color-sombra-aviso)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-aviso focus-visible:ring-offset-2`}
        >
            Continuar · {caso.id}
            <ChevronRight size={16} stroke={2} />
        </Link>
    );
};
