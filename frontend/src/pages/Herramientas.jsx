import { useMemo } from 'react';
import { Spinner } from '@/components/Spinner';
import { EmptyState, ErrorState } from '@/components/Estados';
import { SinRonda } from '@/components/SinRonda';
import { Tarjeta, Titulo } from '@/components/Tarjeta';
import { CopiarLista } from '@/components/herramientas/CopiarLista';
import { FiltroAudiencia } from '@/components/FiltroAudiencia';
import { SelectorRonda } from '@/components/SelectorRonda';
import { useLocalStorageState } from '@/hooks/useLocalStorageState';
import { FilaHerramienta } from '@/components/herramientas/FilaHerramienta';
import { useRonda } from '@/hooks/useRonda';
import { useSesion } from '@/hooks/useSesion';
import { PERMISOS } from '@/utils/permisos';
import { useContenido, useHerramientas } from '@/hooks/useValidacion';
import { Apps, Filter } from 'tesela/react';

const Herramientas = () => {
    const { puede } = useSesion();
    const { ronda, cargando } = useRonda();
    const { data, isPending, error, refetch } = useHerramientas(ronda?.id);
    const [audiencia, setAudiencia] = useLocalStorageState('validacion.herramientas.audiencia', 'todas');
    const { data: contenido } = useContenido();
    const errores = contenido?.errores ?? [];
    const grupos = useMemo(() => {
        const mapa = new Map();
        (data ?? [])
            .filter((h) => audiencia === 'todas' || h.audiencia === audiencia)
            .forEach((h) => mapa.set(h.sistema, [...(mapa.get(h.sistema) ?? []), h]));
        return [...mapa.entries()].sort(([a], [b]) => a.localeCompare(b, 'es'));
    }, [data, audiencia]);

    if (!ronda && !cargando) return <SinRonda />;
    if (isPending) return <Spinner pantalla />;
    if (error) return <ErrorState mensaje={error.message} onReintentar={refetch} />;
    if (!data?.length) return <EmptyState icono={Apps} titulo="El contenido todavía no declara herramientas" />;

    return (
        <>
            <div className="flex flex-wrap items-center gap-3">
                <FiltroAudiencia valor={audiencia} onCambiar={setAudiencia} />
                <SelectorRonda />
            </div>
            <Tarjeta>
                <Titulo
                    descripcion="Recomienda por herramienta si se despliega, con aviso o se aplaza; la sugerida sale de sus casos y fallas. Quien aprueba decide en «Aprobaciones»."
                    accion={<CopiarLista grupos={grupos} />}
                >
                    Herramientas
                </Titulo>
                {errores.length > 0 && (
                    <div className="tipo-media text-xs text-error-fuerte">
                        <p className="tipo-negrita">Archivos de contenido que no se pudieron leer</p>
                        <ul className="mt-1 list-disc pl-5">
                            {errores.map((e) => <li key={e} className="break-words">{e}</li>)}
                        </ul>
                    </div>
                )}
            </Tarjeta>
            {!grupos.length && <EmptyState icono={Filter} titulo="No hay herramientas de este tipo" />}
            {grupos.map(([sistema, herramientas]) => (
                <Tarjeta key={sistema}>
                    <h2 className="mb-3 tipo-negrita text-base text-primario">{sistema}</h2>
                    <ul className="flex flex-col gap-3">
                        {herramientas.map((h) => (
                            <FilaHerramienta key={`${h.id}-${h.decision?.actualizado ?? ''}`} herramienta={h} rondaId={ronda.id} editable={puede(PERMISOS.gestionarFallas)} />
                        ))}
                    </ul>
                </Tarjeta>
            ))}
        </>
    );
};

export default Herramientas;
