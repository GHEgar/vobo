import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchInstancia } from '@/services/validacion';

const VACIA = { nombre: '', descripcion: '', proyectos: [] };

export const useInstancia = () => {
    const { data } = useQuery({
        queryKey: ['instancia'],
        queryFn: fetchInstancia,
        staleTime: 60 * 60 * 1000,
        retry: 1,
    });
    return data ?? VACIA;
};

export const useProyectos = () => useInstancia().proyectos;

export const useMetaInstancia = () => {
    const { nombre, descripcion } = useInstancia();
    useEffect(() => {
        if (nombre) document.title = nombre;
        const meta = document.querySelector('meta[name="description"]');
        if (meta && descripcion) meta.setAttribute('content', descripcion);
    }, [nombre, descripcion]);
};
