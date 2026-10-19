import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchInstancia } from '@/services/validacion';
import { useClaveProyecto, useProyecto } from '@/hooks/useProyecto';
import { nombreVisible, tituloDocumento } from '@/utils/marca';

const VACIA = {
    producto: '',
    nombre: '',
    descripcion: '',
    logo: null,
    favicon: '',
    color_tema: '',
    entrada: { titulo: '', mensaje: '' },
    proyectos: [],
    sistemas: [],
    proyecto: null,
};

export const useInstancia = () => {
    const proyecto = useClaveProyecto();
    const { data } = useQuery({
        queryKey: ['instancia', proyecto],
        queryFn: () => fetchInstancia(proyecto),
        staleTime: 60 * 60 * 1000,
        retry: 1,
    });
    return data ?? VACIA;
};

export const useSistemas = () => useInstancia().sistemas;

export const useNombreProyecto = () => {
    const { producto } = useInstancia();
    const { proyecto, proyectos } = useProyecto();
    return nombreVisible(producto, proyecto, proyectos);
};

const fijarAtributo = (selector, atributo, valor) => {
    const elemento = document.querySelector(selector);
    if (elemento && valor) elemento.setAttribute(atributo, valor);
};

const fijarMeta = (nombre, valor) => {
    if (!valor) return;
    let meta = document.querySelector(`meta[name="${nombre}"]`);
    if (!meta) {
        meta = document.createElement('meta');
        meta.setAttribute('name', nombre);
        document.head.appendChild(meta);
    }
    meta.setAttribute('content', valor);
};

export const useMetaInstancia = () => {
    const { producto, nombre, descripcion, favicon, color_tema: colorTema } = useInstancia();
    useEffect(() => {
        const titulo = tituloDocumento(producto, nombre);
        if (titulo) document.title = titulo;
        fijarAtributo('meta[name="description"]', 'content', descripcion);
        fijarMeta('theme-color', colorTema);
        const icono = document.querySelector('link[rel="icon"]');
        if (icono && favicon && icono.getAttribute('href') !== favicon) {
            icono.removeAttribute('type');
            icono.setAttribute('href', favicon);
        }
    }, [producto, nombre, descripcion, favicon, colorTema]);
};
