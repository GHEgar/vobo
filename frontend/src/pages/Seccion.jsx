import { useState } from 'react';
import { Link, useParams } from 'react-router';
import { ChevronLeft } from 'tesela/react';
import { Chip } from '@/components/Chip';
import { Galeria } from '@/components/Galeria';
import { Spinner } from '@/components/Spinner';
import { EmptyState, ErrorState } from '@/components/Estados';
import { Modal } from '@/components/Modal';
import { Tarjeta } from '@/components/Tarjeta';
import { Tooltip } from '@/components/Tooltip';
import { useProgreso } from '@/hooks/useMisCasos';
import { useLocalStorageState } from '@/hooks/useLocalStorageState';
import { useSesion } from '@/hooks/useSesion';
import { useHerramientas } from '@/hooks/useValidacion';
import { DECISIONES, ESTADOS_RESULTADO, HOY } from '@/utils/etiquetas';
import { estadoDe } from '@/utils/progreso';

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

const BotonInfo = ({ texto, pulso, onClick }) => (
    <span className="relative inline-flex">
        {pulso && <span aria-hidden="true" className="absolute inset-0 animate-ping rounded-full bg-aviso/40" />}
        <button
            type="button"
            onClick={onClick}
            className={`relative inline-flex h-[30px] items-center rounded-full border px-4 tipo-negrita text-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primario focus-visible:ring-offset-2 ${pulso ? 'border-aviso bg-aviso text-white' : 'border-gris bg-transparent text-texto-tenue hover:border-primario hover:text-primario'}`}
        >
            {texto}
        </button>
    </span>
);

const Seccion = () => {
    const { seccionId } = useParams();
    const { ronda, datos, cargando, error, reintentar } = useProgreso();
    const { usuario } = useSesion();
    const [vistas, setVistas] = useLocalStorageState(`validacion.secciones-vistas.${usuario.email}`, []);
    const [modal, setModal] = useState(null);

    if (cargando) return <Spinner pantalla />;
    if (error) return <ErrorState mensaje={error.message} onReintentar={reintentar} />;

    const seccion = datos.indice.secciones.get(seccionId);
    if (!seccion) return <EmptyState titulo="Sección no encontrada" />;
    const progreso = { hechos: seccion.casos.filter((c) => estadoDe(datos.estados, c.id) !== 'pendiente').length, total: seccion.casos.length };
    const pulso = progreso.hechos < progreso.total && !vistas.includes(seccion.id);
    const abrirInfo = () => {
        setModal('info');
        if (!vistas.includes(seccion.id)) setVistas([...vistas, seccion.id]);
    };

    return (
        <>
            <div className="flex flex-wrap items-center justify-between gap-3">
                <Link to="/" className="inline-flex w-fit items-center gap-1 tipo-negrita text-sm text-primario hover:underline"><ChevronLeft size={16} stroke={2} />Inicio</Link>
                <div className="flex flex-wrap items-center gap-2">
                    <BotonInfo texto="Qué cambia" pulso={pulso} onClick={abrirInfo} />
                    {seccion.media.length > 0 && <BotonInfo texto={`Cómo se ve (${seccion.media.length})`} onClick={() => setModal('media')} />}
                </div>
            </div>
            <Tarjeta>
                <div className="flex flex-wrap items-center gap-2">
                    <Chip tono="marca">{seccion.sistema}</Chip>
                </div>
                <h1 className="mt-3 tipo-negrita text-xl text-texto md:text-2xl">{seccion.titulo}</h1>
                <p className="mt-1 tipo-media text-sm text-texto-tenue">{progreso.hechos} de {progreso.total} casos marcados</p>
                <ul className="mt-5 flex flex-col gap-2">
                    {seccion.casos.map((c) => {
                        const estado = ESTADOS_RESULTADO[estadoDe(datos.estados, c.id)];
                        return (
                            <li key={c.id}>
                                <Link to={`/caso/${encodeURIComponent(c.id)}`} className="flex flex-wrap items-center justify-between gap-2 rounded-2xl bg-fondo px-5 py-3 hover:bg-primario-claro">
                                    <span className="flex flex-col">
                                        <span className="tipo-media text-[11px] text-texto-apagado">{c.id}</span>
                                        <span className="tipo-negrita text-sm text-texto">{c.titulo}</span>
                                    </span>
                                    <Chip tono={estado.tono}>{estado.texto}</Chip>
                                </Link>
                            </li>
                        );
                    })}
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
            <Modal abierto={modal === 'media'} titulo="Cómo se ve" onCerrar={() => setModal(null)} ancho="max-w-5xl">
                <Galeria items={seccion.media} />
            </Modal>
        </>
    );
};

export default Seccion;
