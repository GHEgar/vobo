import { useMemo, useState } from 'react';
import { Link } from 'react-router';
import { Button } from '@/components/Button';
import { Spinner } from '@/components/Spinner';
import { EmptyState, ErrorState } from '@/components/Estados';
import { PestanasVerticales } from '@/components/PestanasVerticales';
import { SinRonda } from '@/components/SinRonda';
import { Tarjeta, Titulo } from '@/components/Tarjeta';
import { TarjetaAprobacion } from '@/components/aprobaciones/TarjetaAprobacion';
import { useProyectos } from '@/hooks/useInstancia';
import { useLocalStorageState } from '@/hooks/useLocalStorageState';
import { useRonda } from '@/hooks/useRonda';
import { useSesion } from '@/hooks/useSesion';
import { useAprobaciones, useContenido, useHerramientas, useRegistrarAprobaciones } from '@/hooks/useValidacion';
import { FILTROS, agruparPorSistema, combinar, contar } from '@/utils/aprobaciones';
import { PERMISOS } from '@/utils/permisos';
import { indexarContenido } from '@/utils/progreso';

const Aprobaciones = () => {
    const { ronda, cargando } = useRonda();
    const { puede } = useSesion();
    const herramientas = useHerramientas(ronda?.id);
    const aprobaciones = useAprobaciones(ronda?.id);
    const contenido = useContenido();
    const registrar = useRegistrarAprobaciones();
    const [filtro, setFiltro] = useLocalStorageState('validacion.aprobaciones.filtro', 'pendientes');
    const [pestana, setPestana] = useState(null);
    const puedeAprobar = puede(PERMISOS.aprobar);
    const proyectos = useProyectos();

    const items = useMemo(() => combinar(herramientas.data ?? [], aprobaciones.data), [herramientas.data, aprobaciones.data]);
    const indice = useMemo(() => (contenido.data ? indexarContenido(contenido.data) : null), [contenido.data]);

    if (!ronda && !cargando) return <SinRonda />;
    if (herramientas.isPending || aprobaciones.isPending || !indice) return <Spinner pantalla />;
    const error = herramientas.error || aprobaciones.error;
    if (error) return <ErrorState mensaje={error.message} onReintentar={() => { herramientas.refetch(); aprobaciones.refetch(); }} />;

    const cuentas = contar(items);
    const criterio = FILTROS.find((f) => f.clave === filtro) ?? FILTROS[0];
    const grupos = agruparPorSistema(proyectos, items.filter((h) => criterio.acepta(h.aprobacion.estado)));
    const decidir = (tipo, objetivo, estado, comentario) => registrar.mutate({
        ronda_id: ronda.id,
        items: [{ tipo, objetivo_id: objetivo, estado, comentario }],
    });

    return (
        <>
            <Tarjeta>
                <Titulo
                    descripcion={puedeAprobar ? 'Aprueba o rechaza cada herramienta o cada característica. Coordinación recomienda; tú decides qué sale a producción.' : 'Solo lectura: las decisiones las toma quien tiene el rol de aprobación.'}
                    accion={<Link to={`/acta?ronda=${ronda.id}`} className="inline-flex h-[30px] items-center rounded-full border border-primario px-4 tipo-negrita text-xs text-primario hover:bg-primario-suave">Generar acta</Link>}
                >
                    Aprobaciones
                </Titulo>
                <div className="flex w-fit flex-wrap gap-1 rounded-full bg-fondo p-1" role="group" aria-label="Filtrar por estado">
                    {FILTROS.map((f) => (
                        <Button key={f.clave} label={`${f.texto} (${cuentas[f.clave]})`} small variant={criterio.clave === f.clave ? 'primary' : 'link'} pressed={criterio.clave === f.clave} onClick={() => setFiltro(f.clave)} />
                    ))}
                </div>
                {registrar.error && <p className="mt-3 tipo-media text-sm text-error-fuerte">{registrar.error.message}</p>}
            </Tarjeta>
            {grupos.length ? (
                <PestanasVerticales
                    id="aprobaciones"
                    pestanas={grupos.map((g) => ({ clave: g.clave, nombre: g.nombre, contador: `${g.herramientas.length}` }))}
                    elegida={grupos.some((g) => g.clave === pestana) ? pestana : grupos[0].clave}
                    onElegir={setPestana}
                >
                    {(activa) => (
                        <ul className="flex flex-col gap-3">
                            {grupos.find((g) => g.clave === activa.clave).herramientas.map((h) => (
                                <TarjetaAprobacion key={h.id} herramienta={h} indice={indice} puedeAprobar={puedeAprobar} onDecidir={decidir} guardando={registrar.isPending} />
                            ))}
                        </ul>
                    )}
                </PestanasVerticales>
            ) : (
                <EmptyState titulo="No hay herramientas con este filtro" />
            )}
        </>
    );
};

export default Aprobaciones;
