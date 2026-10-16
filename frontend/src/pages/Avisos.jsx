import { useState } from 'react';
import { Link } from 'react-router';
import { Button } from '@/components/Button';
import { Chip } from '@/components/Chip';
import { Spinner } from '@/components/Spinner';
import { EmptyState, ErrorState } from '@/components/Estados';
import { Tarjeta, Titulo } from '@/components/Tarjeta';
import { TextoConEnlaces } from '@/components/TextoConEnlaces';
import { NuevoAviso } from '@/components/avisos/NuevoAviso';
import { useAvisos, useMarcarAvisoLeido, useMarcarAvisosLeidos } from '@/hooks/useAvisos';
import { useSesion } from '@/hooks/useSesion';
import { useProyecto } from '@/hooks/useProyecto';
import { claveDeEnlace, conProyecto } from '@/utils/enlaces';
import { PERMISOS } from '@/utils/permisos';
import { formatearFecha, formatearRelativa } from '@/utils/formato';
import { Bell } from 'tesela/react';

const AvisoItem = ({ aviso, onLeer }) => {
    const { proyectos } = useProyecto();
    const [abierto, setAbierto] = useState(false);
    const nuevo = !aviso.leido;
    const leer = () => {
        if (nuevo) onLeer(aviso.id);
    };
    const alternar = () => {
        setAbierto(!abierto);
        leer();
    };

    return (
        <li className={`min-w-0 rounded-2xl p-5 shadow-[0px_3px_12px_var(--color-sombra-tenue)] ${nuevo ? 'bg-primario-suave ring-1 ring-primario-borde' : 'bg-white'}`}>
            <button
                type="button"
                onClick={alternar}
                aria-expanded={abierto}
                className="flex w-full flex-wrap items-start justify-between gap-2 bg-transparent p-0 text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primario"
            >
                <span className="flex min-w-0 flex-col gap-1">
                    <span className="flex flex-wrap items-center gap-2">
                        {nuevo && <Chip tono="marca">Nuevo</Chip>}
                        <span className={`text-base ${nuevo ? 'tipo-negrita text-primario' : 'tipo-media text-texto'}`}>{aviso.titulo}</span>
                    </span>
                    <span className="tipo-media text-xs text-texto-apagado">
                        {aviso.autor_nombre || aviso.autor_email} · <time dateTime={aviso.creado} title={formatearFecha(aviso.creado)}>{formatearRelativa(aviso.creado)}</time>
                    </span>
                </span>
                <span className="tipo-negrita text-xs text-primario">{abierto ? 'Ocultar' : 'Leer'}</span>
            </button>
            <p className={`mt-3 whitespace-pre-line wrap-anywhere tipo-regular text-[15px]/6 text-texto ${abierto ? '' : 'line-clamp-2'}`}>
                <TextoConEnlaces texto={aviso.mensaje} />
            </p>
            {aviso.caso_id && (
                <Link to={conProyecto(`/caso/${encodeURIComponent(aviso.caso_id)}`, claveDeEnlace(aviso.proyecto_clave, proyectos))} onClick={leer} className="mt-3 inline-flex tipo-negrita text-sm text-primario hover:underline">
                    Ir al caso {aviso.caso_id}
                </Link>
            )}
        </li>
    );
};

const Avisos = () => {
    const { puede } = useSesion();
    const { data, isPending, error, refetch } = useAvisos();
    const marcar = useMarcarAvisoLeido();
    const marcarTodos = useMarcarAvisosLeidos();
    const [nuevo, setNuevo] = useState(false);
    const [enviados, setEnviados] = useState(0);
    const coordina = puede(PERMISOS.gestionarFallas);
    const sinLeer = (data ?? []).filter((a) => !a.leido).length;

    const acciones = (
        <div className="flex flex-wrap gap-2">
            {sinLeer > 0 && <Button label="Marcar todos como leídos" variant="outline" small loading={marcarTodos.isPending} onClick={() => marcarTodos.mutate()} />}
            {coordina && <Button label="Nuevo aviso" small onClick={() => setNuevo(true)} />}
        </div>
    );

    return (
        <>
            <Tarjeta>
                <Titulo descripcion={sinLeer ? `Tienes ${sinLeer} sin leer.` : 'Lo que coordinación te ha escrito sobre tus reportes.'} accion={acciones}>
                    Avisos
                </Titulo>
                <p role="status" className="tipo-media text-sm text-pasa">
                    {enviados ? `Aviso enviado a ${enviados === 1 ? '1 persona' : `${enviados} personas`}.` : ''}
                </p>
                {(marcar.error || marcarTodos.error) && (
                    <p className="tipo-media text-xs text-error-fuerte">{(marcar.error || marcarTodos.error).message}</p>
                )}
            </Tarjeta>
            {isPending && <Spinner pantalla />}
            {error && <ErrorState mensaje={error.message} onReintentar={refetch} />}
            {data && !data.length && (
                <EmptyState icono={Bell} titulo="No tienes avisos" descripcion="Cuando coordinación atienda uno de tus reportes o quiera decirte algo, lo verás aquí." />
            )}
            {data?.length > 0 && (
                <ul className="flex flex-col gap-4">
                    {data.map((a) => <AvisoItem key={a.id} aviso={a} onLeer={(id) => marcar.mutate(id)} />)}
                </ul>
            )}
            {coordina && (
                <NuevoAviso
                    abierto={nuevo}
                    onCerrar={() => setNuevo(false)}
                    onEnviado={(total) => setEnviados(total)}
                />
            )}
        </>
    );
};

export default Avisos;
