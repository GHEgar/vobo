import { useContext } from 'react';
import { SesionContext } from '@/contexts/SesionContext';

export const useSesion = () => {
    const contexto = useContext(SesionContext);
    if (!contexto) throw new Error('useSesion debe usarse dentro de SesionProvider');
    return contexto;
};
