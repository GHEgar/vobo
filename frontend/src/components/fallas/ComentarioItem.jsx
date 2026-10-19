import { useState } from 'react';
import { Link } from 'react-router';
import { Alert, Check, Copy } from 'tesela/react';
import { Chip } from '@/components/Chip';
import { TextoConEnlaces } from '@/components/TextoConEnlaces';
import { Dato, Detalles } from '@/components/fallas/Detalles';
import { EstadoCampo, Franja } from '@/components/fallas/Franja';
import { PlazoCampo } from '@/components/fallas/PlazoCampo';
import { Resolucion } from '@/components/fallas/Resolucion';
import { Seguimiento } from '@/components/fallas/Seguimiento';
import { useActualizarComentario } from '@/hooks/useValidacion';
import { useRuta } from '@/hooks/useProyecto';
import { ESTADOS_COMENTARIO } from '@/utils/etiquetas';
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

export const ComentarioItem = ({ comentario: c, editable }) => {
    const ruta = useRuta();
    const actualizar = useActualizarComentario();
    const gestionable = editable && c.id !== null && c.id !== undefined;
    const cambiar = (cambios) => actualizar.mutate({ id: c.id, ...cambios });

    return (
        <li className="min-w-0 rounded-2xl border border-borde bg-white p-5">
            <div className="flex flex-wrap items-center gap-2">
                <Chip tono={c.tipo === 'no_pude' ? 'aviso' : 'marca'}>
                    {c.tipo === 'no_pude' && <Alert size={16} className="shrink-0" />}
                    {c.tipo === 'no_pude' ? 'No pudo probarlo' : `Paso ${c.paso + 1}`}
                </Chip>
                {c.sistema && <Chip tono="marca">{c.sistema}</Chip>}
                <CopiarTaiga comentario={c} />
            </div>
            <h3 className="mt-2 wrap-anywhere tipo-negrita text-base">
                <Link to={ruta(`/caso/${encodeURIComponent(c.caso_id)}`)} className="text-primario hover:underline">
                    {c.caso_id} · {c.caso_titulo}
                </Link>
            </h3>
            <p className="mt-2 whitespace-pre-line wrap-anywhere tipo-regular text-[15px]/6 text-texto"><TextoConEnlaces texto={c.comentario} /></p>
            <Franja etiqueta={`Estado y plazo del comentario en ${c.caso_id}`}>
                <EstadoCampo
                    id={`estado-comentario-${c.id}`}
                    valor={c.estado}
                    estados={ESTADOS_COMENTARIO}
                    editable={gestionable}
                    etiqueta="Estado del comentario"
                    onCambiar={(estado) => cambiar({ estado })}
                >
                    <Resolucion verbo="Resuelto" en={c.resuelto_en} por={c.resuelto_por_nombre || c.resuelto_por} desde={c.creado} />
                </EstadoCampo>
                <PlazoCampo
                    id={`comentario-${c.id}`}
                    plazo={c.plazo}
                    responsable={c.plazo_por_nombre || c.plazo_por}
                    resuelto={c.estado === 'resuelto'}
                    editable={gestionable}
                    onCambiar={(plazo) => cambiar({ plazo })}
                    textoVencido="Vencido"
                />
            </Franja>
            {actualizar.error && <p className="mt-2 tipo-media text-xs text-error-fuerte">{actualizar.error.message}</p>}
            <Detalles>
                <Dato termino="Paso">{c.tipo === 'no_pude' ? 'No pudo probarlo' : `${c.paso + 1}. ${c.paso_texto || ''}`}</Dato>
                <Dato termino="Escribió">{c.autor || c.usuario_email}</Dato>
                <Dato termino="Fecha">{formatearFecha(c.actualizado)}</Dato>
                <Dato termino="Ronda">{c.ronda_nombre}</Dato>
            </Detalles>
            {c.id != null && <Seguimiento objeto="comentario" id={c.id} eventos={c.seguimiento} estados={ESTADOS_COMENTARIO} editable={gestionable} />}
        </li>
    );
};
