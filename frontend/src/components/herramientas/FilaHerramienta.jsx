import { useState } from 'react';
import { Link } from 'react-router';
import { Button } from '@/components/Button';
import { Chip } from '@/components/Chip';
import { ProgressBar } from '@/components/ProgressBar';
import { SelectField } from '@/components/Field';
import { useDecidirHerramienta } from '@/hooks/useValidacion';
import { DECISIONES, HOY, SEVERIDADES, SUGERENCIAS, opciones } from '@/utils/etiquetas';
import { useRuta } from '@/hooks/useProyecto';

const CONTROL = 'block h-[40px] w-full rounded-[8px] border border-transparent bg-fondo px-4 tipo-media text-[13px] text-primario placeholder-texto-placeholder hover:border-primario hover:bg-white focus:bg-white focus:outline-none focus:ring-1 focus:ring-primario';

export const FilaHerramienta = ({ herramienta, rondaId, editable }) => {
    const ruta = useRuta();
    const decidir = useDecidirHerramienta();
    const sugerida = herramienta.sugerencia === 'sin_probar' ? 'pendiente' : herramienta.sugerencia;
    const [decision, setDecision] = useState(herramienta.decision?.decision ?? sugerida);
    const [motivo, setMotivo] = useState(herramienta.decision?.motivo ?? '');
    const ejecutados = herramienta.casos.pasa + herramienta.casos.falla;
    const fallas = Object.entries(herramienta.fallas_abiertas).filter(([, n]) => n > 0);
    const cambiado = decision !== (herramienta.decision?.decision ?? 'pendiente') || motivo !== (herramienta.decision?.motivo ?? '');

    return (
        <li className="grid grid-cols-1 gap-4 rounded-2xl bg-fondo p-4 lg:grid-cols-[minmax(0,1.3fr)_minmax(0,1fr)_minmax(0,1.6fr)] lg:items-center">
            <div className="flex flex-col gap-2">
                <div className="flex flex-wrap items-center gap-2">
                    <span className="tipo-negrita text-sm text-texto">{herramienta.nombre}</span>
                    <Chip tono={HOY[herramienta.hoy].tono}>{HOY[herramienta.hoy].texto}</Chip>
                </div>
                <Link to={ruta(`/seccion/${herramienta.seccion_id}`)} className="w-fit tipo-media text-xs text-primario hover:underline">
                    {herramienta.seccion_titulo}
                </Link>
            </div>
            <div className="flex flex-col gap-2">
                <span className="tipo-media text-xs text-texto-tenue">
                    {ejecutados} de {herramienta.casos_total} casos
                    {herramienta.casos.no_pude > 0 && ` · ${herramienta.casos.no_pude} sin poder probar`}
                </span>
                <ProgressBar hechos={ejecutados} total={herramienta.casos_total} delgada />
                <span className="tipo-media text-[11px] text-texto-apagado">{herramienta.sugerencia_motivo}</span>
                <div className="flex flex-wrap gap-1">
                    <Chip tono={SUGERENCIAS[herramienta.sugerencia].tono} title={herramienta.sugerencia_motivo}>
                        Sugerida: {SUGERENCIAS[herramienta.sugerencia].texto}
                    </Chip>
                    {fallas.map(([severidad, n]) => (
                        <Chip key={severidad} tono={SEVERIDADES[severidad].tono}>{n} {SEVERIDADES[severidad].texto.toLowerCase()}</Chip>
                    ))}
                </div>
            </div>
            {!editable && (
                <div className="flex flex-col gap-1">
                    <Chip tono={DECISIONES[herramienta.decision?.decision ?? 'pendiente'].tono}>
                        {DECISIONES[herramienta.decision?.decision ?? 'pendiente'].texto}
                    </Chip>
                    {herramienta.decision?.motivo && <span className="tipo-media text-xs text-texto-tenue">{herramienta.decision.motivo}</span>}
                </div>
            )}
            {editable && <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                <SelectField
                    id={`decision-${herramienta.id}`}
                    aria-label={`Recomendación para ${herramienta.nombre}`}
                    value={decision}
                    onChange={(e) => setDecision(e.target.value)}
                    options={opciones(DECISIONES)}
                    className="sm:w-[160px] sm:shrink-0"
                />
                <input
                    aria-label={`Motivo para ${herramienta.nombre}`}
                    placeholder="Motivo"
                    value={motivo}
                    onChange={(e) => setMotivo(e.target.value)}
                    className={CONTROL}
                />
                <Button
                    label="Guardar"
                    small
                    variant="outline"
                    disabled={!cambiado}
                    loading={decidir.isPending}
                    onClick={() => decidir.mutate({ herramientaId: herramienta.id, ronda_id: rondaId, decision, motivo })}
                />
            </div>}
            {decidir.error && <p className="tipo-media text-xs text-error-fuerte lg:col-span-3">{decidir.error.message}</p>}
        </li>
    );
};
