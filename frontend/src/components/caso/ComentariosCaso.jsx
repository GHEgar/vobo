import { Tarjeta, Titulo } from '@/components/Tarjeta';
import { useComentariosCaso } from '@/hooks/useValidacion';
import { formatearFecha } from '@/utils/formato';

export const ComentariosCaso = ({ casoId, rondaId, deTodos }) => {
    const { data } = useComentariosCaso(casoId, rondaId);
    if (!data?.length) return null;
    return (
        <Tarjeta>
            <Titulo descripcion={deTodos ? 'De todo el equipo, los más recientes primero.' : 'Los tuyos, los más recientes primero.'}>Comentarios</Titulo>
            <ul className="flex flex-col gap-2">
                {data.map((c) => (
                    <li key={`${c.usuario_email}-${c.tipo}-${c.paso}`} className="rounded-2xl bg-fondo px-5 py-3">
                        <p className="tipo-media text-xs text-texto-apagado">
                            {c.autor} · {c.tipo === 'no_pude' ? 'No pudo probarlo' : `Paso ${c.paso + 1}`} · {formatearFecha(c.actualizado)}
                        </p>
                        <p className="mt-1 whitespace-pre-line tipo-regular text-sm/6 text-texto">{c.comentario}</p>
                    </li>
                ))}
            </ul>
        </Tarjeta>
    );
};
