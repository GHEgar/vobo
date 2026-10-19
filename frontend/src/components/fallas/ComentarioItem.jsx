import { useState } from 'react';
import { Link } from 'react-router';
import { Alert, Check, Copy } from 'tesela/react';
import { Chip } from '@/components/Chip';
import { SelectField } from '@/components/Field';
import { TextoConEnlaces } from '@/components/TextoConEnlaces';
import { PlazoCampo } from '@/components/fallas/PlazoCampo';
import { Resolucion } from '@/components/fallas/Resolucion';
import { Seguimiento } from '@/components/fallas/Seguimiento';
import { useActualizarComentario } from '@/hooks/useValidacion';
import { useRuta } from '@/hooks/useProyecto';
import { ESTADOS_COMENTARIO, opciones } from '@/utils/etiquetas';
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
    const estado = ESTADOS_COMENTARIO[c.estado] ?? ESTADOS_COMENTARIO.nuevo;

    return (
        <li className="min-w-0 rounded-2xl border border-borde bg-white px-5 py-3">
            <div className="flex flex-wrap items-center gap-2">
                <Link to={ruta(`/caso/${encodeURIComponent(c.caso_id)}`)} className="min-w-0 wrap-anywhere tipo-negrita text-sm text-primario hover:underline">
                    {c.caso_id} · {c.caso_titulo}
                </Link>
                <Chip tono={c.tipo === 'no_pude' ? 'aviso' : 'marca'}>
                    {c.tipo === 'no_pude' && <Alert size={16} className="shrink-0" />}
                    {c.tipo === 'no_pude' ? 'No pudo probarlo' : `Paso ${c.paso + 1}`}
                </Chip>
                {!gestionable && <Chip tono={estado.tono}>{estado.texto}</Chip>}
                <CopiarTaiga comentario={c} />
            </div>
            {c.paso_texto && <p className="mt-1 wrap-anywhere tipo-media text-xs text-texto-apagado">{c.paso_texto}</p>}
            <p className="mt-1 whitespace-pre-line wrap-anywhere tipo-regular text-sm text-texto"><TextoConEnlaces texto={c.comentario} /></p>
            <p className="mt-1 tipo-media text-[11px] text-texto-apagado">{c.autor || c.usuario_email} · {formatearFecha(c.actualizado)}</p>
            <div className="mt-2 flex flex-wrap items-end gap-x-4 gap-y-2">
                {gestionable && (
                    <SelectField
                        id={`estado-comentario-${c.id}`}
                        aria-label="Estado del comentario"
                        value={c.estado}
                        onChange={(e) => cambiar({ estado: e.target.value })}
                        options={opciones(ESTADOS_COMENTARIO)}
                        className="w-full sm:w-[180px]"
                    />
                )}
                {(gestionable || c.plazo) && (
                    <PlazoCampo
                        id={`comentario-${c.id}`}
                        plazo={c.plazo}
                        responsable={c.plazo_por_nombre || c.plazo_por}
                        resuelto={c.estado === 'resuelto'}
                        editable={gestionable}
                        onCambiar={(plazo) => cambiar({ plazo })}
                        textoVencido="Vencido"
                    />
                )}
            </div>
            <div className="mt-2"><Resolucion verbo="Resuelto" en={c.resuelto_en} por={c.resuelto_por_nombre || c.resuelto_por} desde={c.creado} /></div>
            {actualizar.error && <p className="mt-2 tipo-media text-xs text-error-fuerte">{actualizar.error.message}</p>}
            {c.id != null && <Seguimiento objeto="comentario" id={c.id} eventos={c.seguimiento} estados={ESTADOS_COMENTARIO} editable={gestionable} />}
        </li>
    );
};
