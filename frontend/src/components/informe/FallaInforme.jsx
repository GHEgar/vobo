import { MediaImagen } from '@/components/MediaImagen';
import { TextoConEnlaces } from '@/components/TextoConEnlaces';
import { Seguimiento } from '@/components/fallas/Seguimiento';
import { Dato, DatosVinculo } from '@/components/informe/Dato';
import { TiemposInforme } from '@/components/informe/TiemposInforme';
import { ESTADOS_FALLA, REPRODUCIBLE, SEVERIDADES } from '@/utils/etiquetas';
import { formatearFecha } from '@/utils/formato';
import { fallaResuelta, pasoDeFalla } from '@/utils/informeFallas';

export const FallaInforme = ({ falla, incluir }) => (
    <article className="min-w-0 break-inside-avoid border-t border-borde py-4">
        <h4 className="wrap-anywhere tipo-negrita text-base">
            #{falla.id} · {falla.seccion_completa ? falla.seccion_titulo : falla.caso_titulo || falla.caso_id}
            <span className="ml-2 tipo-media text-xs text-texto-apagado">{falla.caso_id}</span>
        </h4>
        <dl className="mt-2 grid grid-cols-2 gap-x-4 gap-y-2 md:grid-cols-4 print:grid-cols-4">
            <Dato termino="Sección">{falla.seccion_titulo || falla.seccion_id}</Dato>
            <Dato termino="Severidad">{SEVERIDADES[falla.severidad]?.texto}</Dato>
            <Dato termino="Estado">{ESTADOS_FALLA[falla.estado]?.texto}</Dato>
            <Dato termino="Tipo">{falla.tipo === 'no_pude' ? 'No pude probarlo' : `Falla · ${REPRODUCIBLE[falla.reproducible]}`}</Dato>
            <Dato termino="Reportó">{falla.usuario_email}</Dato>
            <Dato termino="Fecha">{formatearFecha(falla.creada)}</Dato>
            <Dato termino="Versión visible">{falla.version_visible}</Dato>
            <Dato termino="Dirección">{falla.url}</Dato>
            <DatosVinculo registro={falla} />
            {incluir.has('tiempos') && (
                <TiemposInforme
                    plazo={falla.plazo}
                    responsable={falla.plazo_por_nombre || falla.plazo_por}
                    resueltoEn={falla.resuelta_en}
                    resolvio={falla.resuelta_por_nombre || falla.resuelta_por}
                    desde={falla.creada}
                    resuelto={fallaResuelta(falla)}
                    texto="Vencida"
                />
            )}
        </dl>
        <p className="mt-2 wrap-anywhere text-[13px]"><span className="tipo-negrita">Paso:</span> {pasoDeFalla(falla)}</p>
        <p className="mt-1 whitespace-pre-line wrap-anywhere text-[13px]"><span className="tipo-negrita">Obtenido:</span> <TextoConEnlaces texto={falla.obtenido} /></p>
        {falla.nota_resolucion && <p className="mt-1 wrap-anywhere text-[13px]"><span className="tipo-negrita">Nota de resolución:</span> {falla.nota_resolucion}</p>}
        {incluir.has('evidencias') && falla.evidencias.length > 0 && (
            <ul className="mt-3 flex flex-wrap gap-2">
                {falla.evidencias.map((e) => (
                    <li key={e.id}>
                        <a href={e.url} target="_blank" rel="noreferrer">
                            <MediaImagen url={e.url} alt={`Captura de la falla ${falla.id}`} carga="eager" className="h-24 w-36 rounded-md border border-borde object-cover" />
                        </a>
                    </li>
                ))}
            </ul>
        )}
        {incluir.has('seguimiento') && <Seguimiento objeto="falla" id={falla.id} eventos={falla.seguimiento} estados={ESTADOS_FALLA} />}
    </article>
);
