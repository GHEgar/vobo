import { Spinner } from '@/components/Spinner';
import { ErrorState } from '@/components/Estados';
import { Tarjeta, Titulo } from '@/components/Tarjeta';
import { ComentarioItem } from '@/components/fallas/ComentarioItem';
import { useComentarios } from '@/hooks/useValidacion';

export const ComentariosLista = ({ rondaId, sistema, editable = false }) => {
    const { data, isPending, error, refetch } = useComentarios(rondaId);
    const visibles = (data ?? []).filter((c) => !sistema || c.sistema === sistema);

    return (
        <Tarjeta>
            <Titulo descripcion="Notas que dejaron en los pasos y motivos de «No pude probarlo».">Comentarios</Titulo>
            {isPending && <Spinner />}
            {error && <ErrorState mensaje={error.message} onReintentar={refetch} />}
            {data && !visibles.length && <p className="tipo-media text-sm text-texto-apagado">Sin comentarios con estos filtros.</p>}
            {visibles.length > 0 && (
                <ul className="flex flex-col gap-2">
                    {visibles.map((c) => <ComentarioItem key={c.id ?? `${c.caso_id}-${c.usuario_email}-${c.tipo}-${c.paso}`} comentario={c} editable={editable} />)}
                </ul>
            )}
        </Tarjeta>
    );
};
