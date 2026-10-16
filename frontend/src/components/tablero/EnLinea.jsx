import { Link } from 'react-router';
import { Spinner } from '@/components/Spinner';
import { EmptyState, ErrorState } from '@/components/Estados';
import { Tarjeta, Titulo } from '@/components/Tarjeta';
import { usePresentes } from '@/hooks/useValidacion';
import { iniciales } from '@/utils/formato';
import { describirPresencia, enlacePresencia, haceTiempo } from '@/utils/presencia';
import { useRuta } from '@/hooks/useProyecto';
import { Eye, User } from 'tesela/react';

const PUNTO = {
    activo: { clase: 'bg-exito', texto: 'Activo' },
    inactivo: { clase: 'bg-texto-apagado', texto: 'Inactivo' },
};

const Persona = ({ persona }) => {
    const ruta = useRuta();
    const punto = PUNTO[persona.estado];
    const enlace = enlacePresencia(persona, ruta);
    return (
        <li className="flex items-start gap-3 rounded-2xl bg-fondo p-3">
            <span className="relative flex h-[36px] w-[36px] shrink-0 items-center justify-center rounded-full bg-primario-claro tipo-negrita text-sm text-primario" aria-hidden="true">
                {iniciales(persona.nombre)}
                <span className={`absolute -right-0.5 -bottom-0.5 h-[12px] w-[12px] rounded-full ring-2 ring-white ${punto.clase}`} />
            </span>
            <div className="min-w-0 flex-1">
                <p className="flex flex-wrap items-baseline gap-x-2 tipo-negrita text-sm text-texto">
                    <span>{persona.nombre}{persona.yo && <span className="tipo-media text-texto-apagado"> (tú)</span>}</span>
                    <span className="tipo-media text-[11px] text-texto-apagado">
                        <span className="sr-only">{punto.texto}, </span>{haceTiempo(persona.hace_segundos)}
                    </span>
                </p>
                <p className="mt-0.5 break-words tipo-media text-xs text-texto-tenue">{describirPresencia(persona)}</p>
            </div>
            {enlace && <Link to={enlace} className="shrink-0 self-center tipo-negrita text-xs text-primario hover:underline">Ver caso</Link>}
        </li>
    );
};

export const EnLinea = () => {
    const { data, isPending, error, refetch } = usePresentes();
    const activos = data?.filter((p) => p.estado === 'activo').length ?? 0;

    return (
        <Tarjeta>
            <Titulo icono={Eye} descripcion={data ? `${activos === 1 ? '1 persona activa' : `${activos} personas activas`} ahora · últimos 10 minutos` : 'Últimos 10 minutos'}>En línea</Titulo>
            {isPending && <Spinner />}
            {error && <ErrorState mensaje={error.message} onReintentar={refetch} />}
            {data && !data.length && <EmptyState icono={User} titulo="Nadie conectado en los últimos 10 minutos" />}
            {data?.length > 0 && (
                <ul className="grid grid-cols-1 gap-2 md:grid-cols-2">
                    {data.map((p) => <Persona key={p.email} persona={p} />)}
                </ul>
            )}
        </Tarjeta>
    );
};
