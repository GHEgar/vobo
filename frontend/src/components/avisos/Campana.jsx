import { NavLink } from 'react-router';
import { IconoCampana } from '@/components/Iconos';
import { useAvisosNoLeidos } from '@/hooks/useAvisos';

const etiqueta = (total) => {
    if (!total) return 'Avisos, ninguno sin leer';
    return total === 1 ? 'Avisos, 1 sin leer' : `Avisos, ${total} sin leer`;
};

export const Campana = () => {
    const { data } = useAvisosNoLeidos();
    const total = data?.total ?? 0;

    return (
        <NavLink
            to="/avisos"
            aria-label={etiqueta(total)}
            title="Avisos"
            className={({ isActive }) => `relative flex h-[36px] w-[36px] items-center justify-center rounded-full hover:bg-primario-claro focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primario ${isActive ? 'bg-primario-claro' : 'bg-transparent'}`}
        >
            <IconoCampana className="h-5 w-5" />
            {total > 0 && (
                <span aria-hidden="true" className="absolute -top-0.5 -right-0.5 flex h-[18px] min-w-[18px] items-center justify-center rounded-full bg-error px-1 tipo-negrita text-[10px] text-white">
                    {total > 99 ? '99+' : total}
                </span>
            )}
        </NavLink>
    );
};
