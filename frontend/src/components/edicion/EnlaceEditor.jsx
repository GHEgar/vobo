import { Link } from 'react-router';
import { ArrowRight } from 'tesela/react';
import { useRuta } from '@/hooks/useProyecto';
import { enlaceEditor } from '@/utils/edicion';

export const EnlaceEditor = ({ seccionId, onClick }) => {
    const ruta = useRuta();
    return (
        <p className="tipo-media text-xs text-texto-apagado">
            Historial, procedimientos y cambios estructurales:{' '}
            <Link to={ruta(enlaceEditor(seccionId))} onClick={onClick} className="inline-flex items-center gap-1 tipo-negrita text-primario hover:underline">
                Abrir en el editor
                <ArrowRight size={14} />
            </Link>
        </p>
    );
};
