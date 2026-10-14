import { Chip } from '@/components/Chip';
import { ProgressBar } from '@/components/ProgressBar';
import { useProyectos } from '@/hooks/useInstancia';
import { nombreProyecto, ordenarProyectos } from '@/utils/proyectos';

const Celda = ({ celda }) => {
    if (!celda?.asignado) return <span className="tipo-media text-sm text-gris" title="Sin secciones asignadas en este proyecto">—</span>;
    return (
        <div className="flex min-w-[90px] flex-col gap-1">
            <span className="tipo-negrita text-xs text-texto">{celda.hechos}/{celda.total}</span>
            <ProgressBar hechos={celda.hechos} total={celda.total} delgada />
            {celda.falla > 0 && <span className="tipo-media text-[11px] text-falla">{celda.falla} falla</span>}
        </div>
    );
};

const sumar = (filas, proyecto) => filas.reduce((total, fila) => {
    const celda = fila[proyecto];
    if (!celda?.asignado) return total;
    return { asignado: true, hechos: total.hechos + celda.hechos, total: total.total + celda.total, falla: total.falla + celda.falla };
}, { asignado: false, hechos: 0, total: 0, falla: 0 });

export const MatrizProyectos = ({ tablero }) => {
    const lista = useProyectos();
    const proyectos = ordenarProyectos(lista, tablero.proyectos);
    const personas = tablero.personas.filter((p) => tablero.por_proyecto[p.email]);
    const filas = personas.map((p) => tablero.por_proyecto[p.email]);

    return (
        <div className="overflow-x-auto">
            <table className="w-full border-separate border-spacing-y-2 text-left">
                <thead>
                    <tr>
                        <th scope="col" className="px-3 align-bottom tipo-media text-xs text-texto-apagado">Persona</th>
                        {proyectos.map((p) => {
                            const cobertura = tablero.cobertura[p] ?? 0;
                            return (
                                <th key={p} scope="col" className="px-3 align-bottom">
                                    <span className="block tipo-media text-xs text-texto-apagado">{nombreProyecto(lista, p)}</span>
                                    <span className="mt-1 block">
                                        {cobertura ? (
                                            <span className="tipo-media text-[11px] text-texto-tenue">{cobertura} {cobertura === 1 ? 'persona' : 'personas'}</span>
                                        ) : (
                                            <Chip tono="aviso">Sin nadie</Chip>
                                        )}
                                    </span>
                                </th>
                            );
                        })}
                    </tr>
                </thead>
                <tbody>
                    {personas.map((persona, i) => (
                        <tr key={persona.email} className="bg-fondo">
                            <th scope="row" className="rounded-l-xl px-3 py-3 tipo-negrita text-sm text-texto">
                                {persona.nombre}
                                <span className="block tipo-media text-[11px] text-texto-apagado">{persona.email}</span>
                            </th>
                            {proyectos.map((p, j) => (
                                <td key={p} className={`px-3 py-3 ${j === proyectos.length - 1 ? 'rounded-r-xl' : ''}`}>
                                    <Celda celda={filas[i][p]} />
                                </td>
                            ))}
                        </tr>
                    ))}
                    <tr className="bg-primario-claro">
                        <th scope="row" className="rounded-l-xl px-3 py-3 tipo-negrita text-sm text-primario">Equipo</th>
                        {proyectos.map((p, j) => (
                            <td key={p} className={`px-3 py-3 ${j === proyectos.length - 1 ? 'rounded-r-xl' : ''}`}>
                                <Celda celda={sumar(filas, p)} />
                            </td>
                        ))}
                    </tr>
                </tbody>
            </table>
        </div>
    );
};
