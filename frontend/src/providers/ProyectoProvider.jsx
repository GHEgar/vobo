import { useCallback, useEffect, useMemo } from 'react';
import { useLocation, useNavigate } from 'react-router';
import { useProyectosLista } from '@/hooks/useValidacion';
import { useLocalStorageState } from '@/hooks/useLocalStorageState';
import { ProyectoContext } from '@/contexts/ProyectoContext';
import { Spinner } from '@/components/Spinner';
import { ErrorState } from '@/components/Estados';
import { PARAMETRO_PROYECTO, conProyecto } from '@/utils/enlaces';

const elegirProyecto = (proyectos, enDireccion, guardado) => {
    const porOmision = proyectos.find((p) => p.por_omision) ?? proyectos[0] ?? null;
    return proyectos.find((p) => p.clave === enDireccion)
        ?? proyectos.find((p) => p.clave === guardado)
        ?? porOmision;
};

export const ProyectoProvider = ({ children }) => {
    const { data: proyectos = [], isPending, error, refetch } = useProyectosLista();
    const [guardado, guardar] = useLocalStorageState('validacion.proyecto', null);
    const { pathname, search, hash } = useLocation();
    const navigate = useNavigate();
    const enDireccion = new URLSearchParams(search).get(PARAMETRO_PROYECTO);
    const proyecto = elegirProyecto(proyectos, enDireccion, guardado);
    const clave = proyecto?.clave ?? null;
    const ajeno = proyecto && !proyecto.por_omision;

    useEffect(() => {
        if (clave && clave !== guardado) guardar(clave);
    }, [clave, guardado, guardar]);

    useEffect(() => {
        if (!ajeno || enDireccion === clave) return;
        navigate(conProyecto(`${pathname}${search}${hash}`, clave), { replace: true });
    }, [ajeno, enDireccion, clave, pathname, search, hash, navigate]);

    const elegir = useCallback((nueva) => {
        if (proyectos.some((p) => p.clave === nueva)) navigate(conProyecto('/', nueva));
    }, [proyectos, navigate]);

    const valor = useMemo(() => ({ proyectos, proyecto, clave, elegir }), [proyectos, proyecto, clave, elegir]);

    if (isPending) return <Spinner pantalla />;
    if (error) return <ErrorState mensaje={error.message} onReintentar={refetch} pantalla />;
    return <ProyectoContext value={valor}>{children}</ProyectoContext>;
};
