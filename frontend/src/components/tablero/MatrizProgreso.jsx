import { ProgressBar } from '@/components/ProgressBar';
import { FAMILIAS } from '@/utils/etiquetas';

const Celda = ({ celda }) => {
    if (!celda.total) return <span className="tipo-media text-xs text-gris">—</span>;
    return (
        <div className="flex min-w-[90px] flex-col gap-1">
            <span className="tipo-negrita text-xs text-texto">{celda.hechos}/{celda.total}</span>
            <ProgressBar hechos={celda.hechos} total={celda.total} delgada />
            {(celda.falla > 0 || celda.no_pude > 0) && (
                <span className="tipo-media text-[11px]">
                    {celda.falla > 0 && <span className="text-error-fuerte">{celda.falla} falla </span>}
                    {celda.no_pude > 0 && <span className="text-aviso-texto">{celda.no_pude} no pudo</span>}
                </span>
            )}
        </div>
    );
};

export const MatrizProgreso = ({ familias, personas }) => (
    <div className="overflow-x-auto">
        <table className="w-full border-separate border-spacing-y-2 text-left">
            <thead>
                <tr>
                    <th scope="col" className="px-3 tipo-media text-xs text-texto-apagado">Persona</th>
                    {familias.map((f) => (
                        <th key={f} scope="col" className="px-3 tipo-media text-xs text-texto-apagado" title={FAMILIAS[f]}>
                            {f} · {FAMILIAS[f]}
                        </th>
                    ))}
                </tr>
            </thead>
            <tbody>
                {personas.map((p) => (
                    <tr key={p.email} className="bg-fondo">
                        <th scope="row" className="rounded-l-xl px-3 py-3 tipo-negrita text-sm text-texto">
                            {p.nombre}
                            <span className="block tipo-media text-[11px] text-texto-apagado">{p.email}</span>
                        </th>
                        {p.celdas.map((c, i) => (
                            <td key={c.familia} className={`px-3 py-3 ${i === p.celdas.length - 1 ? 'rounded-r-xl' : ''}`}>
                                <Celda celda={c} />
                            </td>
                        ))}
                    </tr>
                ))}
            </tbody>
        </table>
    </div>
);
