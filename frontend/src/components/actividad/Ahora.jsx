import { User } from 'tesela/react';
import { Spinner } from '@/components/Spinner';
import { EmptyState, ErrorState } from '@/components/Estados';
import { Persona } from '@/components/actividad/Persona';
import { useRondas } from '@/hooks/useValidacion';

const ORDEN = { activo: 0, inactivo: 1 };

export const Ahora = ({ consulta, onNavegar }) => {
    const { data, isPending, error, refetch } = consulta;
    const { data: rondas = [] } = useRondas();
    const nombreRonda = (id) => (id ? rondas.find((r) => r.id === id)?.nombre ?? `Ronda ${id}` : null);
    const personas = [...(data ?? [])].sort((a, b) => ORDEN[a.estado] - ORDEN[b.estado]);

    if (isPending) return <Spinner />;
    if (error) return <ErrorState mensaje={error.message} onReintentar={refetch} />;
    if (!personas.length) {
        return <EmptyState icono={User} titulo="Nadie conectado" descripcion="Aquí aparece quien haya usado la aplicación en los últimos 10 minutos." />;
    }
    return (
        <ul className="flex flex-col gap-2">
            {personas.map((p) => (
                <Persona key={p.email} persona={p} ronda={nombreRonda(p.ronda_id)} detallada onNavegar={onNavegar} />
            ))}
        </ul>
    );
};
