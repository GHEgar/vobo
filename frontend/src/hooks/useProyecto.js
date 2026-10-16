import { useCallback, useContext } from 'react';
import { ProyectoContext } from '@/contexts/ProyectoContext';
import { conProyecto } from '@/utils/enlaces';

export const useProyecto = () => {
    const contexto = useContext(ProyectoContext);
    if (!contexto) throw new Error('useProyecto debe usarse dentro de ProyectoProvider');
    return contexto;
};

export const useClaveProyecto = () => useContext(ProyectoContext)?.clave ?? null;

export const useRuta = () => {
    const contexto = useContext(ProyectoContext);
    const clave = contexto?.proyecto && !contexto.proyecto.por_omision ? contexto.clave : null;
    return useCallback((ruta, otra) => conProyecto(ruta, otra === undefined ? clave : otra), [clave]);
};
