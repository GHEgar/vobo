import { useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router';
import { Spinner } from '@/components/Spinner';
import { ErrorState } from '@/components/Estados';
import { Checkbox } from '@/components/Checkbox';
import { EncabezadoImpreso } from '@/components/EncabezadoImpreso';
import { BOTON_IMPRESO as BOTON, HojaImpresa } from '@/components/HojaImpresa';
import { MediaImagen } from '@/components/MediaImagen';
import { TextoConEnlaces } from '@/components/TextoConEnlaces';
import { useLocalStorageState } from '@/hooks/useLocalStorageState';
import { useRonda } from '@/hooks/useRonda';
import { useComentarios, useFallas } from '@/hooks/useValidacion';
import { ESTADOS_FALLA, REPRODUCIBLE, SEVERIDADES } from '@/utils/etiquetas';
import { formatearFecha } from '@/utils/formato';
import { CLAVE_COMENTARIOS, comentariosDeFalla, describirFiltros, filtrosDe, pasoDeFalla, resumenFallas } from '@/utils/informeFallas';
import { ArrowLeft, Document, Filter } from 'tesela/react';

const TablaConteo = ({ titulo, filas, total }) => (
    <table className="w-full border-collapse text-left text-[13px]">
        <thead>
            <tr className="tipo-negrita text-[11px] text-texto-apagado">
                <th scope="col" className="py-2 pr-3">{titulo}</th>
                <th scope="col" className="py-2 text-right">Fallas</th>
            </tr>
        </thead>
        <tbody>
            {filas.map((f) => (
                <tr key={f.valor} className="border-t border-borde">
                    <td className="py-1.5 pr-3">{f.texto}</td>
                    <td className="py-1.5 text-right tipo-negrita">{f.total}</td>
                </tr>
            ))}
            <tr className="border-t border-texto-apagado tipo-negrita">
                <td className="py-1.5 pr-3">Total</td>
                <td className="py-1.5 text-right">{total}</td>
            </tr>
        </tbody>
    </table>
);

const Dato = ({ termino, children }) => (
    <div>
        <dt className="tipo-media text-[11px] text-texto-apagado">{termino}</dt>
        <dd className="wrap-anywhere text-[13px]">{children || '—'}</dd>
    </div>
);

const ComentariosFalla = ({ comentarios }) => (
    <div className="mt-3 min-w-0 rounded-lg border border-borde px-3 py-2">
        <p className="tipo-negrita text-[13px]">Comentarios</p>
        {comentarios.length ? (
            <ul className="mt-1 flex flex-col gap-1">
                {comentarios.map((c) => (
                    <li key={`${c.usuario_email}-${c.tipo}-${c.paso}`} className="whitespace-pre-line wrap-anywhere text-[13px]">
                        <span className="tipo-media text-texto-apagado">{formatearFecha(c.actualizado)} · {c.autor || c.usuario_email}:</span>
                        {' '}
                        <TextoConEnlaces texto={c.comentario} />
                    </li>
                ))}
            </ul>
        ) : (
            <p className="mt-1 text-[13px] text-texto-apagado">Sin comentarios.</p>
        )}
    </div>
);

const DetalleFalla = ({ falla, comentarios }) => (
    <article className="min-w-0 break-inside-avoid border-t border-borde py-4">
        <h3 className="wrap-anywhere tipo-negrita text-base">
            #{falla.id} · {falla.seccion_completa ? falla.seccion_titulo : falla.caso_titulo || falla.caso_id}
            <span className="ml-2 tipo-media text-xs text-texto-apagado">{falla.caso_id}</span>
        </h3>
        <dl className="mt-2 grid grid-cols-2 gap-x-4 gap-y-2 md:grid-cols-4 print:grid-cols-4">
            <Dato termino="Sección">{falla.seccion_titulo || falla.seccion_id}</Dato>
            <Dato termino="Severidad">{SEVERIDADES[falla.severidad]?.texto}</Dato>
            <Dato termino="Estado">{ESTADOS_FALLA[falla.estado]?.texto}</Dato>
            <Dato termino="Tipo">{falla.tipo === 'no_pude' ? 'No pude probarlo' : `Falla · ${REPRODUCIBLE[falla.reproducible]}`}</Dato>
            <Dato termino="Reportó">{falla.usuario_email}</Dato>
            <Dato termino="Fecha">{formatearFecha(falla.creada)}</Dato>
            <Dato termino="Versión visible">{falla.version_visible}</Dato>
            <Dato termino="Dirección">{falla.url}</Dato>
        </dl>
        <p className="mt-2 wrap-anywhere text-[13px]"><span className="tipo-negrita">Paso:</span> {pasoDeFalla(falla)}</p>
        <p className="mt-1 whitespace-pre-line wrap-anywhere text-[13px]"><span className="tipo-negrita">Obtenido:</span> <TextoConEnlaces texto={falla.obtenido} /></p>
        {falla.nota_resolucion && <p className="mt-1 wrap-anywhere text-[13px]"><span className="tipo-negrita">Nota de resolución:</span> {falla.nota_resolucion}</p>}
        {falla.evidencias.length > 0 && (
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
        {comentarios && <ComentariosFalla comentarios={comentarios} />}
    </article>
);

const InformeFallas = () => {
    const [params, setParams] = useSearchParams();
    const filtros = useMemo(() => filtrosDe(params), [params]);
    const conComentarios = params.get('comentarios') === '1';
    const [, recordar] = useLocalStorageState(CLAVE_COMENTARIOS, false);
    const { rondas } = useRonda();
    const ronda = rondas.find((r) => String(r.id) === filtros.ronda);
    const { data, isPending, error, refetch } = useFallas(filtros);
    const comentarios = useComentarios(filtros.ronda, conComentarios);
    const alternar = (activo) => {
        recordar(activo);
        setParams((previos) => {
            const nuevos = new URLSearchParams(previos);
            if (activo) nuevos.set('comentarios', '1');
            else nuevos.delete('comentarios');
            return nuevos;
        }, { replace: true });
    };
    const [generado] = useState(() => formatearFecha(new Date().toISOString()));
    const resumen = useMemo(() => resumenFallas(data ?? []), [data]);

    if (isPending || (conComentarios && comentarios.isPending)) return <Spinner pantalla />;
    const fallo = error || (conComentarios && comentarios.error);
    if (fallo) return <ErrorState mensaje={fallo.message} onReintentar={error ? refetch : comentarios.refetch} pantalla />;
    const deFalla = (f) => (conComentarios ? comentariosDeFalla(f, comentarios.data ?? []) : null);

    const acciones = (
        <>
            <div className="flex flex-wrap gap-2">
                <Link to={`/fallas?${params}`} className={`${BOTON} bg-borde text-texto-tenue`}><ArrowLeft size={18} className="shrink-0" />Volver</Link>
                <button type="button" onClick={() => window.print()} className={`${BOTON} bg-primario text-white`}><Document size={18} className="shrink-0" />Imprimir / guardar PDF</button>
            </div>
            <Checkbox id="informe-comentarios" checked={conComentarios} onChange={alternar}>Incluir comentarios</Checkbox>
        </>
    );

    return (
        <HojaImpresa acciones={acciones}>
            <EncabezadoImpreso titulo="Informe de fallas">
                <p className="mt-1 tipo-media text-sm text-texto-tenue">
                    Ronda: {ronda ? `${ronda.nombre}${ronda.snapshot ? ` (${ronda.snapshot})` : ''}` : 'Todas'} · Generado: {generado}
                </p>
                <p className="mt-1 tipo-media text-xs text-texto-apagado">
                    Filtros: {describirFiltros(filtros, ronda).map(([k, v]) => `${k}: ${v}`).join(' · ')}
                </p>
            </EncabezadoImpreso>
            <section className="mt-8 break-inside-avoid-page">
                <h2 className="border-b border-borde pb-1 tipo-negrita text-lg text-primario">Resumen</h2>
                {data.length ? (
                    <div className="mt-2 grid grid-cols-1 gap-6 md:grid-cols-3 print:grid-cols-3">
                        <TablaConteo titulo="Severidad" filas={resumen.severidad} total={data.length} />
                        <TablaConteo titulo="Estado" filas={resumen.estado} total={data.length} />
                        <TablaConteo titulo="Sección" filas={resumen.seccion} total={data.length} />
                    </div>
                ) : (
                    <p className="mt-2 flex items-center gap-2 text-sm text-texto-tenue"><Filter size={16} className="shrink-0" />No hay fallas con estos filtros.</p>
                )}
            </section>
            {data.length > 0 && (
                <section className="mt-8">
                    <h2 className="border-b border-borde pb-1 tipo-negrita text-lg text-primario">Detalle ({data.length})</h2>
                    {data.map((f) => <DetalleFalla key={f.id} falla={f} comentarios={deFalla(f)} />)}
                </section>
            )}
        </HojaImpresa>
    );
};

export default InformeFallas;
