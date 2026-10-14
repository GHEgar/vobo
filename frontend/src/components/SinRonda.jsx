import { Link } from 'react-router';
import { EmptyState } from '@/components/Estados';
import { useSesion } from '@/hooks/useSesion';
import { PERMISOS } from '@/utils/permisos';

export const SinRonda = () => {
    const { puede } = useSesion();
    return (
        <EmptyState
            titulo="Todavía no hay una ronda abierta"
            descripcion="Cuando coordinación abra la primera ronda aparecerán aquí tus casos."
            accion={puede(PERMISOS.gestionarFallas) && (
                <Link to="/rondas" className="tipo-negrita text-sm text-primario hover:underline">Abrir una ronda</Link>
            )}
        />
    );
};
