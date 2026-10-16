import { Link } from 'react-router';
import { Chip } from '@/components/Chip';
import { ProgressBar } from '@/components/ProgressBar';
import { Spinner } from '@/components/Spinner';
import { EmptyState, ErrorState } from '@/components/Estados';
import { SinRonda } from '@/components/SinRonda';
import { Tarjeta, Titulo } from '@/components/Tarjeta';
import { MatrizProgreso } from '@/components/tablero/MatrizProgreso';
import { MatrizSistemas } from '@/components/tablero/MatrizSistemas';
import { FiltroAudiencia } from '@/components/FiltroAudiencia';
import { SelectorRonda } from '@/components/SelectorRonda';
import { Button } from '@/components/Button';
import { useLocalStorageState } from '@/hooks/useLocalStorageState';
import { Veredicto } from '@/components/tablero/Veredicto';
import { useRonda } from '@/hooks/useRonda';
import { useSesion } from '@/hooks/useSesion';
import { useTablero } from '@/hooks/useValidacion';
import { SEVERIDADES } from '@/utils/etiquetas';
import { LineChart } from 'tesela/react';

const Tablero = () => {
    const { ronda, cargando: cargandoRonda } = useRonda();
    const { ve } = useSesion();
    const [audiencia, setAudiencia] = useLocalStorageState('validacion.tablero.audiencia', 'todas');
    const { data, isPending, error, refetch } = useTablero(ronda?.id, audiencia);
    const [vista, setVista] = useLocalStorageState('validacion.tablero.vista', 'familia');

    if (!ronda && !cargandoRonda) return <SinRonda />;
    if (isPending) return <Spinner pantalla />;
    if (error) return <ErrorState mensaje={error.message} onReintentar={refetch} />;

    return (
        <>
            <div className="flex flex-wrap items-center gap-3">
                <FiltroAudiencia valor={audiencia} onCambiar={setAudiencia} />
                <SelectorRonda />
            </div>
            <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
                <Veredicto tablero={data} />
                <Tarjeta>
                    <Titulo
                        descripcion="Las cerradas ya no cuentan para la salida."
                        accion={ve('fallas') && <Link to="/fallas" className="tipo-negrita text-sm text-primario hover:underline">Ver fallas</Link>}
                    >
                        Fallas abiertas
                    </Titulo>
                    <ul className="grid grid-cols-2 gap-3">
                        {data.fallas.map((f) => (
                            <li key={f.severidad} className="flex flex-col gap-1 rounded-2xl bg-fondo p-4">
                                <span className="w-fit"><Chip tono={SEVERIDADES[f.severidad].tono}>{SEVERIDADES[f.severidad].texto}</Chip></span>
                                <span className="tipo-negrita text-2xl text-texto">{f.abiertas}</span>
                                <span className="tipo-media text-[11px] text-texto-apagado">{f.total} reportadas en total</span>
                            </li>
                        ))}
                    </ul>
                    <div className="mt-5">
                        <p className="tipo-media text-xs text-texto-tenue">
                            {data.casos_ejecutados} de {data.casos_total} casos ejecutados en la ronda
                        </p>
                        <div className="mt-2"><ProgressBar hechos={data.casos_ejecutados} total={data.casos_total} /></div>
                    </div>
                </Tarjeta>
            </div>
            <Tarjeta>
                <Titulo
                    descripcion={vista === 'proyecto' ? 'Casos marcados por persona y sistema; «—» es un sistema que no tiene asignado.' : 'Casos marcados por persona y familia.'}
                    accion={(
                        <div className="flex gap-1 rounded-full bg-fondo p-1" role="group" aria-label="Agrupar el equipo">
                            <Button label="Por familia" small variant={vista === 'familia' ? 'primary' : 'link'} pressed={vista === 'familia'} onClick={() => setVista('familia')} />
                            <Button label="Por sistema" small variant={vista === 'proyecto' ? 'primary' : 'link'} pressed={vista === 'proyecto'} onClick={() => setVista('proyecto')} />
                        </div>
                    )}
                >
                    Equipo
                </Titulo>
                {vista === 'proyecto' && <MatrizSistemas tablero={data} />}
                {vista !== 'proyecto' && (data.personas.length ? (
                    <MatrizProgreso familias={data.familias} personas={data.personas} />
                ) : (
                    <EmptyState icono={LineChart} titulo="Nadie ha marcado casos en esta ronda" />
                ))}
            </Tarjeta>
        </>
    );
};

export default Tablero;
