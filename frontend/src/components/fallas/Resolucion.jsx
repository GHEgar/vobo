import { formatearFecha } from '@/utils/formato';
import { duracion } from '@/utils/seguimiento';

export const Resolucion = ({ en, por, desde, verbo = 'Resuelta' }) => {
    if (!en) return null;
    const tiempo = duracion(desde, en);
    return (
        <p className="tipo-media text-xs text-pasa">
            {verbo} por {por || '—'} el {formatearFecha(en)}{tiempo && ` · tardó ${tiempo}`}
        </p>
    );
};
