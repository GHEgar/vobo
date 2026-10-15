import { useState } from 'react';
import { Link } from 'react-router';
import { Check, Copy } from 'tesela/react';
import { Chip } from '@/components/Chip';
import { Spinner } from '@/components/Spinner';
import { ErrorState } from '@/components/Estados';
import { Tarjeta, Titulo } from '@/components/Tarjeta';
import { useComentarios } from '@/hooks/useValidacion';
import { formatearFecha } from '@/utils/formato';
import { copiarTexto } from '@/utils/portapapeles';

const paraTaiga = (c) => [
    `[${c.caso_id}] ${c.caso_titulo} — ${c.tipo === 'no_pude' ? 'no pudo probarlo' : `paso ${c.paso + 1}`}`,
    c.comentario,
    `Ronda: ${c.ronda_nombre} · ${c.autor || c.usuario_email} · ${formatearFecha(c.actualizado)}`,
].join('\n');

const CopiarTaiga = ({ comentario }) => {
    const [copiado, setCopiado] = useState(false);
    return (
        <button
            type="button"
            onClick={async () => setCopiado(await copiarTexto(paraTaiga(comentario)))}
            className="ml-auto inline-flex shrink-0 items-center gap-1 bg-transparent p-0 tipo-negrita text-xs text-primario underline underline-offset-4 hover:text-primario-hover"
        >
            {copiado ? <Check size={14} stroke={2} /> : <Copy size={14} stroke={2} />}
            {copiado ? 'Copiado' : 'Copiar para Taiga'}
        </button>
    );
};

export const ComentariosLista = ({ rondaId, sistema }) => {
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
                    {visibles.map((c) => (
                        <li key={`${c.caso_id}-${c.usuario_email}-${c.tipo}-${c.paso}`} className="rounded-2xl bg-fondo px-5 py-3">
                            <div className="flex flex-wrap items-center gap-2">
                                <Link to={`/caso/${encodeURIComponent(c.caso_id)}`} className="tipo-negrita text-sm text-primario hover:underline">
                                    {c.caso_id} · {c.caso_titulo}
                                </Link>
                                <Chip tono={c.tipo === 'no_pude' ? 'aviso' : 'marca'}>
                                    {c.tipo === 'no_pude' ? 'No pudo probarlo' : `Paso ${c.paso + 1}`}
                                </Chip>
                                <CopiarTaiga comentario={c} />
                            </div>
                            {c.paso_texto && <p className="mt-1 tipo-media text-xs text-texto-apagado">{c.paso_texto}</p>}
                            <p className="mt-1 whitespace-pre-line tipo-regular text-sm text-texto">{c.comentario}</p>
                            <p className="mt-1 tipo-media text-[11px] text-texto-apagado">{c.autor || c.usuario_email} · {formatearFecha(c.actualizado)}</p>
                        </li>
                    ))}
                </ul>
            )}
        </Tarjeta>
    );
};
