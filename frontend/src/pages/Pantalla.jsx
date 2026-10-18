import { lazy, Suspense, useEffect } from 'react';
import { useParams } from 'react-router';
import { Escalado, Indicador, Mensaje } from '@/components/pantalla/Escalado';
import { useCursorOculto, useDatosPantalla, usePantallaConfig, useRotacion } from '@/hooks/usePantalla';
import { useVersionNueva } from '@/hooks/useVersionNueva';

const VistaGeneral = lazy(() => import('@/components/pantalla/VistaGeneral'));
const VistaGrafo = lazy(() => import('@/components/pantalla/VistaGrafo'));

const VISTAS = { general: VistaGeneral, grafo: VistaGrafo };

const Contenido = ({ token }) => {
    const config = usePantallaConfig(token);
    const datos = useDatosPantalla(token, config.isSuccess);
    const vistas = (config.data?.vistas ?? []).filter((v) => VISTAS[v]);
    const indice = useRotacion(vistas.length, config.data?.segundos ?? 20);

    useEffect(() => {
        if (config.data?.nombre) document.title = config.data.nombre;
    }, [config.data?.nombre]);

    const revocada = config.error?.estado === 404 || datos.error?.estado === 404;
    if (revocada) return <Mensaje titulo="Esta pantalla no está disponible" detalle="El enlace no existe, se regeneró o se desactivó." />;
    if (!config.data || !datos.data) {
        if (config.error || datos.error) return <Mensaje titulo="Sin conexión" detalle="Reintentando…" />;
        return <Mensaje titulo="Cargando…" />;
    }
    const Vista = VISTAS[vistas[indice]] ?? VistaGeneral;
    const sinConexion = Boolean(datos.error) || Boolean(config.error);

    return (
        <>
            <Suspense fallback={null}>
                <Vista token={token} config={config.data} datos={datos.data} sinConexion={sinConexion} segundos={config.data.segundos} />
            </Suspense>
            <Indicador vistas={vistas} actual={indice} sinConexion={sinConexion} />
        </>
    );
};

const Pantalla = () => {
    const { token } = useParams();
    const cursorOculto = useCursorOculto();
    const versionNueva = useVersionNueva();

    useEffect(() => {
        if (versionNueva) window.location.reload();
    }, [versionNueva]);

    return (
        <Escalado cursorOculto={cursorOculto}>
            <Contenido token={token} />
        </Escalado>
    );
};

export default Pantalla;
