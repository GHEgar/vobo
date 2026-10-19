import { TextoConEnlaces } from '@/components/TextoConEnlaces';
import { Seguimiento } from '@/components/fallas/Seguimiento';
import { Dato } from '@/components/informe/Dato';
import { TiemposInforme } from '@/components/informe/TiemposInforme';
import { ESTADOS_COMENTARIO } from '@/utils/etiquetas';
import { formatearFecha } from '@/utils/formato';
import { comentarioResuelto } from '@/utils/informeFallas';

export const ComentarioInforme = ({ comentario: c, incluir }) => (
    <article className="min-w-0 break-inside-avoid border-t border-borde py-4">
        <h4 className="wrap-anywhere tipo-negrita text-base">
            {c.tipo === 'no_pude' ? 'No pudo probarlo' : `Comentario en el paso ${c.paso + 1}`} · {c.caso_titulo || c.caso_id}
            <span className="ml-2 tipo-media text-xs text-texto-apagado">{c.caso_id}</span>
        </h4>
        <dl className="mt-2 grid grid-cols-2 gap-x-4 gap-y-2 md:grid-cols-4 print:grid-cols-4">
            <Dato termino="Reportó">{c.autor || c.usuario_email}</Dato>
            <Dato termino="Fecha">{formatearFecha(c.actualizado)}</Dato>
            <Dato termino="Estado">{ESTADOS_COMENTARIO[c.estado]?.texto}</Dato>
            <Dato termino="Ronda">{c.ronda_nombre}</Dato>
            {incluir.has('tiempos') && (
                <TiemposInforme
                    plazo={c.plazo}
                    responsable={c.plazo_por_nombre || c.plazo_por}
                    resueltoEn={c.resuelto_en}
                    resolvio={c.resuelto_por_nombre || c.resuelto_por}
                    desde={c.creado}
                    resuelto={comentarioResuelto(c)}
                />
            )}
        </dl>
        {c.paso_texto && <p className="mt-2 wrap-anywhere text-[13px]"><span className="tipo-negrita">Paso:</span> {c.paso_texto}</p>}
        <p className="mt-1 whitespace-pre-line wrap-anywhere text-[13px]"><span className="tipo-negrita">Comentario:</span> <TextoConEnlaces texto={c.comentario} /></p>
        {incluir.has('seguimiento') && c.id != null && <Seguimiento objeto="comentario" id={c.id} eventos={c.seguimiento} estados={ESTADOS_COMENTARIO} />}
    </article>
);
