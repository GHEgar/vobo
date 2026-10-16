import { ProgressBar } from '@/components/ProgressBar';
import { Spinner } from '@/components/Spinner';
import { EmptyState, ErrorState } from '@/components/Estados';
import { Modal } from '@/components/Modal';
import { Continuar } from '@/components/inicio/Continuar';
import { SelectorRonda } from '@/components/SelectorRonda';
import { CuentasPrueba } from '@/components/inicio/CuentasPrueba';
import { PestanasSistemas } from '@/components/inicio/PestanasSistemas';
import { AvancePorSistema } from '@/components/inicio/PorSistema';
import { SinRonda } from '@/components/SinRonda';
import { AccionesSeccion } from '@/components/edicion/AccionesSeccion';
import { ModalSeccion } from '@/components/edicion/ModalSeccion';
import { useState } from 'react';
import { useSearchParams } from 'react-router';
import { useSistemas } from '@/hooks/useInstancia';
import { useProgreso } from '@/hooks/useMisCasos';
import { useLocalStorageState } from '@/hooks/useLocalStorageState';
import { useRecordarScroll } from '@/hooks/useRecordarScroll';
import { useSesion } from '@/hooks/useSesion';
import { useEdicion } from '@/hooks/useEdicion';
import { useSeccionesEditables } from '@/hooks/useSeccionesEditables';
import { formatearPorcentaje } from '@/utils/formato';
import { casoParaContinuar } from '@/utils/progreso';
import { agruparSeccionesPorSistema } from '@/utils/sistemas';
import { Layers } from 'tesela/react';

const ID_PESTANAS = 'sistemas';

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
    const listaSistemas = useSistemas();
    const { activo: editando } = useEdicion();
    const [pedido, setPedido] = useState(null);
    const editables = useSeccionesEditables(datos?.secciones ?? null, editando);
    useRecordarScroll(`inicio:${params.get('sistema') ?? pestanaGuardada ?? ''}`, Boolean(ronda) && !cargando && !error);

    if (!ronda && !cargando) return <SinRonda />;
    if (cargando) return <Spinner pantalla />;
    if (error) return <ErrorState mensaje={error.message} onReintentar={reintentar} />;

    const { total, asignadas } = datos;
    const sistemas = agruparSeccionesPorSistema(listaSistemas, editables.secciones);
    const objetivo = casoParaContinuar(datos);
    const existe = (clave) => sistemas.some((g) => g.clave === clave);
    const pestana = [params.get('sistema'), params.get('proyecto'), pestanaGuardada].find(existe) ?? pestanaInicial(sistemas, objetivo);
    const elegir = (clave) => {
        setPestanaGuardada(clave);
        setParams((actuales) => {
            const nuevos = new URLSearchParams(actuales);
            nuevos.set('sistema', clave);
            return nuevos;
        }, { replace: true });
    };
    const edicion = editando ? {
        onNueva: (sistema, audiencia) => setPedido({ id: null, inicial: { sistema, audiencia } }),
        acciones: (s, lista) => <AccionesSeccion seccion={s} lista={lista} ids={editables.ids} onUsar={() => elegir(s.sistema)} onEditar={() => setPedido({ id: s.id, titulo: s.titulo })} />,
    } : null;

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
                <h3 className="mt-5 tipo-negrita text-sm text-texto">Por sistema</h3>
                <AvancePorSistema grupos={sistemas} />
            </Modal>
            {sistemas.length ? (
                <PestanasSistemas
                    id={ID_PESTANAS}
                    grupos={sistemas}
                    estados={datos.estados}
                    elegido={pestana}
                    onElegir={elegir}
                    modos={modos}
                    destacado={objetivo?.caso.id}
                    onCambiarModo={(clave, modo) => setModos({ ...modos, [clave]: modo })}
                    edicion={edicion}
                />
            ) : (
                <EmptyState icono={Layers} titulo="Sin secciones" />
            )}
            <ModalSeccion pedido={pedido} onCerrar={() => setPedido(null)} />
        </>
    );
};

export default Inicio;
