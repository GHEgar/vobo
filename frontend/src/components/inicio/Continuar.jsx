import { Link } from 'react-router';
import { ChevronRight } from 'tesela/react';
import { useRuta } from '@/hooks/useProyecto';

const BASE = 'inline-flex h-[38px] items-center gap-1 rounded-full px-5 tipo-negrita text-xs';

export const Continuar = ({ objetivo }) => {
    const ruta = useRuta();
    if (!objetivo) {
        return <span className={`${BASE} cursor-default bg-pasa-fondo text-pasa`}>Terminaste</span>;
    }
    const { caso, paso } = objetivo;
    return (
        <Link
            to={ruta(`/caso/${encodeURIComponent(caso.id)}`)}
            title={`${caso.titulo} · Paso ${paso + 1} de ${caso.pasos.length}`}
            aria-label={`Continuar con ${caso.id}: ${caso.titulo}, paso ${paso + 1} de ${caso.pasos.length}`}
            className={`${BASE} bg-primario text-white transition-shadow hover:bg-primario-hover hover:shadow-[0px_8px_16px_var(--color-sombra)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primario focus-visible:ring-offset-2`}
        >
            Continuar · {caso.id}
            <ChevronRight size={16} />
        </Link>
    );
};
