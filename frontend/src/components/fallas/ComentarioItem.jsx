import { useId, useState } from 'react';
import { Link } from 'react-router';
import { Alert, Check, Copy, Info } from 'tesela/react';
import { Chip } from '@/components/Chip';
import { TextoConEnlaces } from '@/components/TextoConEnlaces';
import { Dato, Detalles } from '@/components/fallas/Detalles';
import { BotonIcono } from '@/components/fallas/BotonIcono';
import { ChipPlazo, EstadoEmergente } from '@/components/fallas/EstadoEmergente';
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
        <BotonIcono
            etiqueta={copiado ? 'Copiado' : 'Copiar para Taiga'}
            icono={copiado ? Check : Copy}
            tono={copiado ? 'exito' : 'neutro'}
            onClick={async () => setCopiado(await copiarTexto(paraTaiga(comentario)))}
        />
    );
};

export const ComentarioItem = ({ comentario: c, editable }) => {
    const ruta = useRuta();
    const actualizar = useActualizarComentario();
    const idDetalles = useId();
    const [detalles, setDetalles] = useState(false);
    const gestionable = editable && c.id !== null && c.id !== undefined;
    const cambiar = (cambios) => actualizar.mutate({ id: c.id, ...cambios });

    return (
        <li className="min-w-0 rounded-2xl border border-borde bg-white p-5">
            <div className="flex items-start justify-between gap-3">
                <div className="flex min-w-0 flex-wrap items-center gap-2">
                    <Chip tono={c.tipo === 'no_pude' ? 'aviso' : 'marca'}>
                        {c.tipo === 'no_pude' && <Alert size={16} className="shrink-0" />}
                        {c.tipo === 'no_pude' ? 'No pudo probarlo' : `Paso ${c.paso + 1}`}
                    </Chip>
                    {c.sistema && <Chip tono="marca">{c.sistema}</Chip>}
                    <ChipPlazo plazo={c.plazo} resuelto={c.estado === 'resuelto'} textoVencido="Vencido" />
                </div>
                <div className="flex shrink-0 items-center gap-1.5 print:hidden">
                    {c.id != null && (
                        <EstadoEmergente
                            id={`comentario-${c.id}`}
                            registro={c}
                            estados={ESTADOS_COMENTARIO}
                            final="resuelto"
                            editable={gestionable}
                            etiqueta="Estado y plazo del comentario"
                            verbo="Resuelto"
                            resolucion={{ en: c.resuelto_en, por: c.resuelto_por_nombre || c.resuelto_por, desde: c.creado }}
                            onCambiar={cambiar}
                            textoVencido="Vencido"
                        />
                    )}
                    <CopiarTaiga comentario={c} />
                    <BotonIcono
                        etiqueta="Detalles"
                        icono={Info}
                        tono={detalles ? 'activo' : 'neutro'}
                        aria-expanded={detalles}
                        aria-controls={idDetalles}
                        onClick={() => setDetalles((actual) => !actual)}
                    />
                </div>
            </div>
            <h3 className="mt-3 wrap-anywhere tipo-negrita text-base">
                <Link to={ruta(`/caso/${encodeURIComponent(c.caso_id)}`)} className="text-primario hover:underline">
                    {c.caso_id} · {c.caso_titulo}
                </Link>
            </h3>
            <p className="mt-2 whitespace-pre-line wrap-anywhere tipo-regular text-[15px]/6 text-texto"><TextoConEnlaces texto={c.comentario} /></p>
            {actualizar.error && <p className="mt-2 tipo-media text-xs text-error-fuerte">{actualizar.error.message}</p>}
            <Detalles id={idDetalles} abierto={detalles}>
                <Dato termino="Paso">{c.tipo === 'no_pude' ? 'No pudo probarlo' : `${c.paso + 1}. ${c.paso_texto || ''}`}</Dato>
                <Dato termino="Escribió">{c.autor || c.usuario_email}</Dato>
                <Dato termino="Fecha">{formatearFecha(c.actualizado)}</Dato>
                <Dato termino="Ronda">{c.ronda_nombre}</Dato>
            </Detalles>
            {c.id != null && <Seguimiento objeto="comentario" id={c.id} eventos={c.seguimiento} estados={ESTADOS_COMENTARIO} editable={gestionable} />}
        </li>
    );
};
