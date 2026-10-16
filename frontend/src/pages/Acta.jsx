import { useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router';
import { CornerDownRight } from 'tesela/react';
import { Spinner } from '@/components/Spinner';
import { ErrorState } from '@/components/Estados';
import { EncabezadoImpreso } from '@/components/EncabezadoImpreso';
import { useInstancia } from '@/hooks/useInstancia';
import { useRonda } from '@/hooks/useRonda';
import { useAprobaciones, useHerramientas } from '@/hooks/useValidacion';
import { actaMarkdown, aprobacionDe, evidenciaDe, pendientesORechazadas, recomendacionDe } from '@/utils/acta';
import { agruparPorSistema, combinar } from '@/utils/aprobaciones';
import { APROBACIONES } from '@/utils/etiquetas';
import { formatearFecha } from '@/utils/formato';
import { useRuta } from '@/hooks/useProyecto';

const BOTON = 'inline-flex h-[36px] items-center rounded-full px-5 tipo-negrita text-sm';

const descargar = (texto, nombre) => {
    const url = URL.createObjectURL(new Blob([texto], { type: 'text/markdown;charset=utf-8' }));
    const enlace = document.createElement('a');
    enlace.href = url;
    enlace.download = nombre;
    enlace.click();
    URL.revokeObjectURL(url);
};

const Acta = () => {
    const [params] = useSearchParams();
    const { rondas, ronda: actual } = useRonda();
    const ronda = rondas.find((r) => String(r.id) === params.get('ronda')) ?? actual;
    const { producto, nombre: instancia, proyecto, sistemas } = useInstancia();
    const nombre = proyecto?.nombre || instancia;
    const ruta = useRuta();
    const herramientas = useHerramientas(ronda?.id);
    const aprobaciones = useAprobaciones(ronda?.id);
    const [generada] = useState(() => formatearFecha(new Date().toISOString()));
    const grupos = useMemo(
        () => agruparPorSistema(sistemas, combinar(herramientas.data ?? [], aprobaciones.data)),
        [sistemas, herramientas.data, aprobaciones.data],
    );

    if (!ronda || herramientas.isPending || aprobaciones.isPending) return <Spinner pantalla />;
    const error = herramientas.error || aprobaciones.error;
    if (error) return <ErrorState mensaje={error.message} pantalla />;

    return (
        <main className="mx-auto max-w-5xl bg-white p-6 text-texto print:max-w-none print:p-0 md:p-10">
            <div className="mb-6 flex flex-wrap gap-2 print:hidden">
                <Link to={ruta('/aprobaciones')} className={`${BOTON} bg-borde text-texto-tenue`}>Volver</Link>
                <button type="button" onClick={() => window.print()} className={`${BOTON} bg-primario text-white`}>Imprimir</button>
                <button type="button" onClick={() => descargar(actaMarkdown({ producto, nombre, ronda, grupos, generada }), `acta-${ronda.nombre.replaceAll(' ', '-').toLowerCase()}.md`)} className={`${BOTON} border border-primario text-primario`}>
                    Descargar .md
                </button>
            </div>
            <EncabezadoImpreso titulo="Acta de aprobación">
                <p className="mt-1 tipo-media text-sm text-texto-tenue">
                    Ronda: {ronda.nombre}{ronda.snapshot ? ` (${ronda.snapshot})` : ''} · Generada: {generada}
                </p>
            </EncabezadoImpreso>
            {grupos.map((g) => (
                <section key={g.clave} className="mt-8 break-inside-avoid-page">
                    <h2 className="border-b border-borde pb-1 tipo-negrita text-lg text-primario">{g.nombre}</h2>
                    <table className="mt-2 w-full border-collapse text-left text-[13px]">
                        <thead>
                            <tr className="tipo-negrita text-[11px] text-texto-apagado">
                                <th scope="col" className="py-2 pr-3">Herramienta</th>
                                <th scope="col" className="py-2 pr-3">Recomendación</th>
                                <th scope="col" className="py-2 pr-3">Evidencia</th>
                                <th scope="col" className="py-2">Aprobación</th>
                            </tr>
                        </thead>
                        <tbody>
                            {g.herramientas.map((h) => {
                                const r = recomendacionDe(h);
                                const a = aprobacionDe(h);
                                const nested = pendientesORechazadas(h);
                                return [
                                    <tr key={h.id} className="border-t border-borde align-top">
                                        <td className="py-2 pr-3 tipo-negrita">{h.nombre}</td>
                                        <td className="py-2 pr-3">{r.texto}<span className="block text-[11px] text-texto-apagado">{r.motivo}</span></td>
                                        <td className="py-2 pr-3">{evidenciaDe(h)}</td>
                                        <td className="py-2">
                                            <span className="tipo-negrita">{a.estado}</span>
                                            {a.quien && <span className="block text-[11px] text-texto-apagado">{a.quien} · {a.fecha}</span>}
                                            {a.comentario && <span className="block text-[11px]">«{a.comentario}»</span>}
                                        </td>
                                    </tr>,
                                    ...nested.map((c) => (
                                        <tr key={`${h.id}-${c.caso_id}`} className="align-top text-[12px] text-texto-tenue">
                                            <td className="py-1 pr-3 pl-4" colSpan={3}><CornerDownRight size={12} stroke={2} className="mr-1 inline-block align-[-1px]" />{c.titulo} <span className="text-texto-apagado">({c.caso_id})</span></td>
                                            <td className="py-1">{APROBACIONES[c.aprobacion.estado].texto}</td>
                                        </tr>
                                    )),
                                ];
                            })}
                        </tbody>
                    </table>
                </section>
            ))}
        </main>
    );
};

export default Acta;
