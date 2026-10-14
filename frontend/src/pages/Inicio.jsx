import { ProgressBar } from '@/components/ProgressBar';
import { Spinner } from '@/components/Spinner';
import { EmptyState, ErrorState } from '@/components/Estados';
import { Modal } from '@/components/Modal';
import { Continuar } from '@/components/inicio/Continuar';
import { SelectorRonda } from '@/components/SelectorRonda';
import { CuentasPrueba } from '@/components/inicio/CuentasPrueba';
import { PestanasProyectos } from '@/components/inicio/PestanasProyectos';
import { AvancePorProyecto } from '@/components/inicio/PorProyecto';
import { SinRonda } from '@/components/SinRonda';
import { useState } from 'react';
import { useSearchParams } from 'react-router';
import { useProyectos } from '@/hooks/useInstancia';
import { useProgreso } from '@/hooks/useMisCasos';
import { useLocalStorageState } from '@/hooks/useLocalStorageState';
import { useSesion } from '@/hooks/useSesion';
import { formatearPorcentaje } from '@/utils/formato';
import { casoParaContinuar } from '@/utils/progreso';
import { agruparPorProyecto } from '@/utils/proyectos';

const ID_PESTANAS = 'proyectos';

const BotonAvance = ({ hechos, total, onClick }) => {
    const porcentaje = total ? Math.round((hechos / total) * 100) : 0;
    return (
        <button
            type="button"
            onClick={onClick}
            aria-label={`Avance: ${porcentaje} por ciento, ${hechos} de ${total} casos`}
            style={{
                border: '1.5px solid transparent',
                background: `linear-gradient(var(--color-fondo-pagina), var(--color-fondo-pagina)) padding-box, linear-gradient(to right, var(--color-pasa-barra) ${porcentaje}%, var(--color-gris-barra) ${porcentaje}%) border-box`,
            }}
            className="inline-flex h-[38px] items-center rounded-full px-5 tipo-negrita text-xs text-texto-tenue hover:text-primario focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primario focus-visible:ring-offset-2"
        >
            Avance · {porcentaje}%
        </button>
    );
};

const pestanaInicial = (grupos, objetivo) => {
    const delContinuar = objetivo && grupos.find((g) => g.secciones.some((s) => s.id === objetivo.caso.seccionId));
    return (delContinuar ?? grupos.find((g) => g.hechos < g.total) ?? grupos[0])?.clave ?? null;
};

const Inicio = () => {
    const { usuario } = useSesion();
    const [modos, setModos] = useLocalStorageState(`validacion.inicio.modos.${usuario.email}`, {});
    const [pestanaGuardada, setPestanaGuardada] = useLocalStorageState(`validacion.inicio.proyecto.${usuario.email}`, null);
    const [params, setParams] = useSearchParams();
    const [verAvance, setVerAvance] = useState(false);
    const { ronda, datos, cargando, error, reintentar } = useProgreso();
    const listaProyectos = useProyectos();

    if (!ronda && !cargando) return <SinRonda />;
    if (cargando) return <Spinner pantalla />;
    if (error) return <ErrorState mensaje={error.message} onReintentar={reintentar} />;

    const { total, secciones, asignadas } = datos;
    const proyectos = agruparPorProyecto(listaProyectos, secciones);
    const objetivo = casoParaContinuar(datos);
    const existe = (clave) => proyectos.some((g) => g.clave === clave);
    const enDireccion = params.get('proyecto');
    const pestana = [enDireccion, pestanaGuardada].find(existe) ?? pestanaInicial(proyectos, objetivo);
    const elegir = (clave) => {
        setPestanaGuardada(clave);
        setParams((actuales) => {
            const nuevos = new URLSearchParams(actuales);
            nuevos.set('proyecto', clave);
            return nuevos;
        }, { replace: true });
    };

    return (
        <>
            <div className="flex flex-wrap items-center justify-between gap-3">
                <SelectorRonda />
                <div className="flex flex-wrap items-center gap-2">
                    <Continuar objetivo={objetivo} />
                    <BotonAvance hechos={total.hechos} total={total.total} onClick={() => setVerAvance(true)} />
                    <CuentasPrueba className="h-[38px]! px-5!" />
                </div>
            </div>
            <Modal abierto={verAvance} titulo={`Avance · ${total.hechos} de ${total.total}`} onCerrar={() => setVerAvance(false)}>
                <p className="mb-3 tipo-media text-xs text-texto-tenue">
                    {asignadas ? 'Casos de las secciones que te asignaron en esta ronda.' : 'Todos los casos de la ronda.'}
                </p>
                <div className="flex items-center gap-4">
                    <ProgressBar {...total} />
                    <span className="shrink-0 tipo-negrita text-sm text-primario">{formatearPorcentaje(total.hechos, total.total)}</span>
                </div>
                <h3 className="mt-5 tipo-negrita text-sm text-texto">Por proyecto</h3>
                <AvancePorProyecto grupos={proyectos} />
            </Modal>
            {proyectos.length ? (
                <PestanasProyectos
                    id={ID_PESTANAS}
                    grupos={proyectos}
                    estados={datos.estados}
                    elegido={pestana}
                    onElegir={elegir}
                    modos={modos}
                    destacado={objetivo?.caso.id}
                    onCambiarModo={(clave, modo) => setModos({ ...modos, [clave]: modo })}
                />
            ) : (
                <EmptyState titulo="Sin secciones" />
            )}
        </>
    );
};

export default Inicio;
