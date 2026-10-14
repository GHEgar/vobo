import { useContext } from 'react';
import { RondaContext } from '@/contexts/RondaContext';

export const useRonda = () => {
    const contexto = useContext(RondaContext);
    if (!contexto) throw new Error('useRonda debe usarse dentro de RondaProvider');
    return contexto;
};
