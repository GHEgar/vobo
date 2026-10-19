import { useMemo } from 'react';
import { Spinner } from '@/components/Spinner';
import { ErrorState } from '@/components/Estados';
import { useParticipacion } from '@/hooks/useInformeFallas';
import { descargarParticipacion, porcentaje, svgParticipacion } from '@/utils/participacion';
import { FileImage, FileVector } from 'tesela/react';

const BOTON = 'inline-flex items-center gap-2 rounded-lg border border-primario bg-white px-3 py-1.5 tipo-media text-sm text-primario disabled:opacity-50';

const Celda = ({ children, encabezado }) => {
    if (encabezado) return <th scope="col" className="py-2 pl-3 align-bottom text-right first:w-1/3 first:pl-0 first:text-left">{children}</th>;
    return <td className="wrap-anywhere py-1.5 pl-3 text-right tipo-negrita first:pl-0 first:text-left first:tipo-media">{children}</td>;
};

const Tabla = ({ titulo, columnas, filas }) => (
    <table className="mt-4 w-full table-fixed border-collapse text-left text-[13px] print:text-[11px]">
        <caption className="text-left tipo-negrita text-sm text-texto">{titulo}</caption>
        <thead>
            <tr className="tipo-negrita text-[11px] text-texto-apagado">
                {columnas.map(([nombre]) => <Celda key={nombre} encabezado>{nombre}</Celda>)}
            </tr>
        </thead>
        <tbody>
            {filas.map((fila) => (
                <tr key={fila.id} className="border-t border-borde">
                    {columnas.map(([nombre, valor]) => <Celda key={nombre}>{valor(fila)}</Celda>)}
                </tr>
            ))}
        </tbody>
    </table>
);

const proyectosDe = (datos) => datos.projects.map((p) => ({
    ...p,
    personas: datos.links.filter((l) => l.project === p.id).length,
}));

const personasDe = (datos) => {
    const nombres = new Map(datos.projects.map((p) => [p.id, p.name]));
    return [...datos.people]
        .sort((a, b) => b.metric - a.metric || a.name.localeCompare(b.name, 'es'))
        .map((p) => ({
            ...p,
            proyectos: datos.links
                .filter((l) => l.person === p.id)
                .sort((a, b) => b.weight - a.weight)
                .map((l) => `${nombres.get(l.project) ?? l.project} (${l.weight})`)
                .join(', '),
        }));
};

export const ParticipacionInforme = ({ claves, ronda, archivo }) => {
    const consulta = useParticipacion(claves, ronda, true);
    const datos = consulta.data;
    const svg = useMemo(() => (datos ? svgParticipacion(datos) : ''), [datos]);
    const estados = datos?.statuses ?? [];
    const columnasProyectos = [
        ['Proyecto', (p) => p.name],
        ['Avance', (p) => porcentaje(p.progress)],
        ...estados.map((e) => [e.label, (p) => p.counts?.[e.key] ?? 0]),
        ['Personas', (p) => p.personas],
    ];
    const columnasPersonas = [
        ['Persona', (p) => p.name],
        ['Casos marcados', (p) => p.metric],
        ['Proyectos', (p) => p.proyectos || '—'],
    ];

    return (
        <section className="mt-8 break-inside-avoid-page" aria-labelledby="informe-participacion">
            <div className="flex flex-wrap items-end justify-between gap-2 border-b border-borde pb-1">
                <h2 id="informe-participacion" className="tipo-negrita text-lg text-primario">Participación</h2>
                <div className="flex gap-2 print:hidden">
                    <button type="button" className={BOTON} disabled={!datos} onClick={() => descargarParticipacion(datos, 'png', archivo)}><FileImage size={16} className="shrink-0" />PNG</button>
                    <button type="button" className={BOTON} disabled={!datos} onClick={() => descargarParticipacion(datos, 'svg', archivo)}><FileVector size={16} className="shrink-0" />SVG</button>
                </div>
            </div>
            <p className="mt-2 tipo-media text-xs text-texto-apagado">
                Proyectos al centro con el anillo de estados de sus casos; cada persona con sus casos marcados y una línea por proyecto, más gruesa cuanto más trabajo.
            </p>
            {consulta.isPending && <div className="mt-4"><Spinner /></div>}
            {consulta.error && <div className="mt-4"><ErrorState mensaje={consulta.error.message} onReintentar={consulta.refetch} /></div>}
            {datos && (
                datos.people.length === 0 ? (
                    <p className="mt-4 text-sm text-texto-tenue">Nadie ha marcado casos todavía con estas opciones.</p>
                ) : (
                    <>
                        <img className="mt-3 block w-full rounded-lg border border-borde" src={`data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`} alt={`Participación de ${datos.people.length} personas en ${datos.projects.length} proyectos`} />
                        <Tabla titulo="Proyectos" columnas={columnasProyectos} filas={proyectosDe(datos)} />
                        <Tabla titulo="Personas" columnas={columnasPersonas} filas={personasDe(datos)} />
                    </>
                )
            )}
        </section>
    );
};
