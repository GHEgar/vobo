import { useState } from 'react';
import { Link, useParams } from 'react-router';
import { ChevronLeft, Edit, InfoCircle, Play, Search } from 'tesela/react';
import { Chip } from '@/components/Chip';
import { ChipResultado } from '@/components/ChipResultado';
import { Galeria } from '@/components/Galeria';
import { Spinner } from '@/components/Spinner';
import { EmptyState, ErrorState } from '@/components/Estados';
import { Modal } from '@/components/Modal';
import { Tarjeta } from '@/components/Tarjeta';
import { Tooltip } from '@/components/Tooltip';
import { AccionesCaso } from '@/components/edicion/AccionesCaso';
import { AgregarFantasma, BarraEdicion } from '@/components/edicion/Editable';
import { contornoEdicion } from '@/utils/edicion';
import { ModalCaso } from '@/components/edicion/ModalCaso';
import { BotonIcono } from '@/components/editor/ListaOrdenable';
import { ModalSeccion } from '@/components/edicion/ModalSeccion';
import { useEdicion } from '@/hooks/useEdicion';
import { useProgreso } from '@/hooks/useMisCasos';
import { useLocalStorageState } from '@/hooks/useLocalStorageState';
import { useRecordarScroll } from '@/hooks/useRecordarScroll';
import { useSesion } from '@/hooks/useSesion';
import { useHerramientas } from '@/hooks/useValidacion';
import { DECISIONES, HOY } from '@/utils/etiquetas';
import { estadoDe } from '@/utils/progreso';
import { useRuta } from '@/hooks/useProyecto';

const ChipsHerramientas = ({ herramientas, rondaId }) => {
    const { data = [] } = useHerramientas(rondaId);
    const decisiones = new Map(data.map((h) => [h.id, h.decision]));
    const propias = herramientas.filter((h) => h.id !== 'general');
    if (!propias.length) return null;
    return (
        <div className="mt-4">
            <div className="flex items-center gap-1">
                <h3 className="tipo-negrita text-sm text-texto">Herramientas</h3>
                <Tooltip text="Cómo está cada herramienta hoy en el build de producción y, si ya se decidió, si se despliega o se aplaza." />
            </div>
            <ul className="mt-2 flex flex-wrap gap-2">
                {propias.map((h) => {
                    const decision = decisiones.get(h.id);
                    return (
                        <li key={h.id} className="flex flex-wrap items-center gap-1">
                            <Chip tono={HOY[h.hoy].tono}>{h.nombre} · {HOY[h.hoy].texto}</Chip>
                            {decision && decision.decision !== 'pendiente' && (
                                <Chip tono={DECISIONES[decision.decision].tono} title={decision.motivo}>
                                    {DECISIONES[decision.decision].texto}
                                </Chip>
                            )}
                        </li>
                    );
                })}
            </ul>
        </div>
    );
};

const BotonInfo = ({ texto, icono: Icono, pulso, onClick }) => (
    <span className="relative inline-flex">
        {pulso && <span aria-hidden="true" className="absolute inset-0 animate-ping rounded-full bg-aviso/40" />}
        <button
            type="button"
            onClick={onClick}
            className={`relative inline-flex h-[30px] items-center gap-1.5 rounded-full border px-4 tipo-negrita text-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primario focus-visible:ring-offset-2 ${pulso ? 'border-aviso bg-aviso text-white' : 'border-gris bg-transparent text-texto-tenue hover:border-primario hover:text-primario'}`}
        >
            <Icono size={16} className="shrink-0" />
            {texto}
        </button>
    </span>
);

const Seccion = () => {
    const ruta = useRuta();
    const { seccionId } = useParams();
    const { ronda, datos, cargando, error, reintentar } = useProgreso();
    const { usuario } = useSesion();
    const [vistas, setVistas] = useLocalStorageState(`validacion.secciones-vistas.${usuario.email}`, []);
    const [modal, setModal] = useState(null);
    const { activo: editando } = useEdicion();
    const [pedidoCaso, setPedidoCaso] = useState(null);
    const [pedidoSeccion, setPedidoSeccion] = useState(null);
    useRecordarScroll(`seccion:${seccionId}`, !cargando && !error);

    if (cargando) return <Spinner pantalla />;
    if (error) return <ErrorState mensaje={error.message} onReintentar={reintentar} />;

    const seccion = datos.indice.secciones.get(seccionId);
    if (!seccion) return <EmptyState icono={Search} titulo="Sección no encontrada" />;
    const progreso = { hechos: seccion.casos.filter((c) => estadoDe(datos.estados, c.id) !== 'pendiente').length, total: seccion.casos.length };
    const pulso = progreso.hechos < progreso.total && !vistas.includes(seccion.id);
    const abrirInfo = () => {
        setModal('info');
        if (!vistas.includes(seccion.id)) setVistas([...vistas, seccion.id]);
    };

    return (
        <>
            <div className="flex flex-wrap items-center justify-between gap-3">
                <Link to="/" className="inline-flex w-fit items-center gap-1 tipo-negrita text-sm text-primario hover:underline"><ChevronLeft size={16} />Inicio</Link>
                <div className="flex flex-wrap items-center gap-2">
                    <BotonInfo texto="Qué cambia" icono={InfoCircle} pulso={pulso} onClick={abrirInfo} />
                    {seccion.media.length > 0 && <BotonInfo texto={`Cómo se ve (${seccion.media.length})`} icono={Play} onClick={() => setModal('media')} />}
                </div>
            </div>
            <Tarjeta>
                <div className={editando ? `${contornoEdicion(true)} rounded-2xl px-5 py-4 pr-14` : ''}>
                    <div className="flex flex-wrap items-center gap-2">
                        <Chip tono="marca">{seccion.sistema}</Chip>
                    </div>
                    <h1 className="mt-3 tipo-negrita text-xl text-texto md:text-2xl">{seccion.titulo}</h1>
                    <p className="mt-1 tipo-media text-sm text-texto-tenue">{progreso.hechos} de {progreso.total} casos marcados</p>
                    {editando && (
                        <BarraEdicion etiqueta={`Acciones de ${seccion.titulo}`}>
                            <BotonIcono etiqueta={`Editar ${seccion.titulo}`} onClick={() => setPedidoSeccion({ id: seccion.id, titulo: seccion.titulo })}><Edit size={16} /></BotonIcono>
                        </BarraEdicion>
                    )}
                </div>
                <ul className="mt-5 flex flex-col gap-2">
                    {seccion.casos.map((c) => {
                        const estado = estadoDe(datos.estados, c.id);
                        return (
                            <li key={c.id} className={`rounded-2xl ${contornoEdicion(editando)}`}>
                                <Link to={ruta(`/caso/${encodeURIComponent(c.id)}`)} className={`flex min-w-0 flex-wrap items-center justify-between gap-2 rounded-2xl bg-fondo px-5 py-3 hover:bg-primario-claro ${editando ? 'pt-14 sm:pt-3 sm:pr-[200px]' : ''}`}>
                                    <span className="flex flex-col">
                                        <span className="tipo-media text-[11px] text-texto-apagado">{c.id}</span>
                                        <span className="tipo-negrita text-sm text-texto">{c.titulo}</span>
                                    </span>
                                    <ChipResultado estado={estado} />
                                </Link>
                                {editando && <AccionesCaso seccionId={seccion.id} caso={c} onPedir={setPedidoCaso} />}
                            </li>
                        );
                    })}
                    {editando && (
                        <li>
                            <AgregarFantasma texto="Agregar caso" onClick={() => setPedidoCaso({ tipo: 'nuevo' })} />
                        </li>
                    )}
                </ul>
            </Tarjeta>
            <Modal abierto={modal === 'info'} titulo={seccion.titulo} onCerrar={() => setModal(null)}>
                <p className="tipo-regular text-[15px]/7 text-texto">{seccion.resumen}</p>
                {seccion.que_cambia.length > 0 && (
                    <>
                        <h2 className="mt-5 tipo-negrita text-sm text-texto">Qué cambia</h2>
                        <ul className="mt-2 flex list-disc flex-col gap-1 pl-5 tipo-media text-sm/6 text-texto-tenue">
                            {seccion.que_cambia.map((linea) => <li key={linea}>{linea}</li>)}
                        </ul>
                    </>
                )}
                {seccion.donde && (
                    <p className="mt-4 tipo-media text-sm text-texto-tenue">
                        Dónde: <a href={seccion.donde} target="_blank" rel="noreferrer" className="break-all text-primario underline">{seccion.donde}</a>
                    </p>
                )}
                <ChipsHerramientas herramientas={seccion.herramientas} rondaId={ronda?.id} />
            </Modal>
            <ModalCaso seccionId={seccion.id} pedido={pedidoCaso} onCerrar={() => setPedidoCaso(null)} />
            <ModalSeccion pedido={pedidoSeccion} onCerrar={() => setPedidoSeccion(null)} />
            <Modal abierto={modal === 'media'} titulo="Cómo se ve" onCerrar={() => setModal(null)} ancho="max-w-5xl">
                <Galeria items={seccion.media} />
            </Modal>
        </>
    );
};

export default Seccion;
