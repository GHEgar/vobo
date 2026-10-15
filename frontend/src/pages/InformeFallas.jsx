import { useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router';
import { Spinner } from '@/components/Spinner';
import { ErrorState } from '@/components/Estados';
import { MediaImagen } from '@/components/MediaImagen';
import { useInstancia } from '@/hooks/useInstancia';
import { useRonda } from '@/hooks/useRonda';
import { useFallas } from '@/hooks/useValidacion';
import { ESTADOS_FALLA, REPRODUCIBLE, SEVERIDADES } from '@/utils/etiquetas';
import { formatearFecha } from '@/utils/formato';
import { describirFiltros, filtrosDe, pasoDeFalla, resumenFallas } from '@/utils/informeFallas';

const BOTON = 'inline-flex h-[36px] items-center rounded-full px-5 tipo-negrita text-sm';

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
        <dd className="break-words text-[13px]">{children || '—'}</dd>
    </div>
);

const DetalleFalla = ({ falla }) => (
    <article className="break-inside-avoid border-t border-borde py-4">
        <h3 className="tipo-negrita text-base">
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
        <p className="mt-2 text-[13px]"><span className="tipo-negrita">Paso:</span> {pasoDeFalla(falla)}</p>
        <p className="mt-1 whitespace-pre-line text-[13px]"><span className="tipo-negrita">Obtenido:</span> {falla.obtenido}</p>
        {falla.nota_resolucion && <p className="mt-1 text-[13px]"><span className="tipo-negrita">Nota de resolución:</span> {falla.nota_resolucion}</p>}
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
    </article>
);

const InformeFallas = () => {
    const [params] = useSearchParams();
    const filtros = useMemo(() => filtrosDe(params), [params]);
    const { rondas } = useRonda();
    const ronda = rondas.find((r) => String(r.id) === filtros.ronda);
    const { nombre } = useInstancia();
    const { data, isPending, error, refetch } = useFallas(filtros);
    const [generado] = useState(() => formatearFecha(new Date().toISOString()));
    const resumen = useMemo(() => resumenFallas(data ?? []), [data]);

    if (isPending) return <Spinner pantalla />;
    if (error) return <ErrorState mensaje={error.message} onReintentar={refetch} pantalla />;

    return (
        <main className="mx-auto max-w-5xl bg-white p-6 text-texto print:max-w-none print:p-0 md:p-10">
            <div className="mb-6 flex flex-wrap gap-2 print:hidden">
                <Link to={`/fallas?${params}`} className={`${BOTON} bg-borde text-texto-tenue`}>Volver</Link>
                <button type="button" onClick={() => window.print()} className={`${BOTON} bg-primario text-white`}>Imprimir / guardar PDF</button>
            </div>
            <h1 className="tipo-negrita text-2xl">{nombre ? `Informe de fallas · ${nombre}` : 'Informe de fallas'}</h1>
            <p className="mt-1 tipo-media text-sm text-texto-tenue">
                Ronda: {ronda ? `${ronda.nombre}${ronda.snapshot ? ` (${ronda.snapshot})` : ''}` : 'Todas'} · Generado: {generado}
            </p>
            <p className="mt-1 tipo-media text-xs text-texto-apagado">
                Filtros: {describirFiltros(filtros, ronda).map(([k, v]) => `${k}: ${v}`).join(' · ')}
            </p>
            <section className="mt-8 break-inside-avoid-page">
                <h2 className="border-b border-borde pb-1 tipo-negrita text-lg text-primario">Resumen</h2>
                {data.length ? (
                    <div className="mt-2 grid grid-cols-1 gap-6 md:grid-cols-3 print:grid-cols-3">
                        <TablaConteo titulo="Severidad" filas={resumen.severidad} total={data.length} />
                        <TablaConteo titulo="Estado" filas={resumen.estado} total={data.length} />
                        <TablaConteo titulo="Sección" filas={resumen.seccion} total={data.length} />
                    </div>
                ) : (
                    <p className="mt-2 text-sm text-texto-tenue">No hay fallas con estos filtros.</p>
                )}
            </section>
            {data.length > 0 && (
                <section className="mt-8">
                    <h2 className="border-b border-borde pb-1 tipo-negrita text-lg text-primario">Detalle ({data.length})</h2>
                    {data.map((f) => <DetalleFalla key={f.id} falla={f} />)}
                </section>
            )}
        </main>
    );
};

export default InformeFallas;
