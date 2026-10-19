import { useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router';
import { Button } from '@/components/Button';
import { SelectField } from '@/components/Field';
import { Spinner } from '@/components/Spinner';
import { EmptyState, ErrorState } from '@/components/Estados';
import { Tarjeta } from '@/components/Tarjeta';
import { ComentariosLista } from '@/components/fallas/ComentariosLista';
import { FallaCard } from '@/components/fallas/FallaCard';
import { TotalesEsfuerzo } from '@/components/fallas/TotalesEsfuerzo';
import { useRonda } from '@/hooks/useRonda';
import { useClaveProyecto, useRuta } from '@/hooks/useProyecto';
import { useSesion } from '@/hooks/useSesion';
import { PERMISOS } from '@/utils/permisos';
import { useComentarios, useContenido, useFallas } from '@/hooks/useValidacion';
import { consulta as aConsulta } from '@/services/api';
import { ESTADOS_FALLA, SEVERIDADES, opciones } from '@/utils/etiquetas';
import { FileText, Filter } from 'tesela/react';

const TIPOS = [
    { valor: 'falla', texto: 'Fallas' },
    { valor: 'no_pude', texto: 'No pude probarlo' },
];

const ENLACE = 'inline-flex h-[30px] items-center gap-1.5 rounded-full border border-primario px-4 tipo-negrita text-xs text-primario hover:bg-primario-suave';

const Fallas = () => {
    const { puede } = useSesion();
    const { rondas } = useRonda();
    const ruta = useRuta();
    const proyecto = useClaveProyecto();
    const { data: contenido } = useContenido();
    const [params] = useSearchParams();
    const [filtros, setFiltros] = useState(() => ({
        sistema: params.get('sistema') ?? '',
        severidad: params.get('severidad') ?? '',
        estado: '',
        tipo: '',
        ronda: '',
    }));
    const [verFiltros, setVerFiltros] = useState(() => Boolean(filtros.sistema || filtros.severidad));
    const activos = Object.values(filtros).filter(Boolean).length;
    const { data, isPending, error, refetch } = useFallas(filtros);
    const { data: comentarios } = useComentarios(filtros.ronda);
    const visibles = useMemo(
        () => [...(data ?? []), ...(comentarios ?? []).filter((c) => c.id != null && (!filtros.sistema || c.sistema === filtros.sistema))],
        [data, comentarios, filtros.sistema],
    );
    const sistemas = useMemo(
        () => [...new Set((contenido?.secciones ?? []).map((s) => s.sistema))].sort().map((s) => ({ valor: s, texto: s })),
        [contenido],
    );
    const fijar = (campo) => (e) => setFiltros({ ...filtros, [campo]: e.target.value });

    return (
        <>
            <Tarjeta>
                <div className="flex flex-wrap items-center justify-between gap-3">
                    <h1 className="tipo-negrita text-lg text-texto">Fallas reportadas</h1>
                    <div className="flex flex-wrap items-center gap-2">
                        <Button
                            small
                            variant={verFiltros ? 'primary' : 'outline'}
                            pressed={verFiltros}
                            aria-controls="filtros-fallas"
                            onClick={() => setVerFiltros(!verFiltros)}
                            icono={<Filter size={16} className="shrink-0" />}
                            label={activos ? `Filtros (${activos})` : 'Filtros'}
                        />
                        <Link to={ruta(`/informe-fallas${aConsulta({ ...filtros, proyectos: proyecto })}`)} title="Informe imprimible, PDF o CSV" className={ENLACE}><FileText size={16} className="shrink-0" />Informe</Link>
                    </div>
                </div>
                {verFiltros && <div id="filtros-fallas" className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
                    <SelectField id="f-ronda" label="Ronda" value={filtros.ronda} onChange={fijar('ronda')} placeholder="Todas" options={rondas.map((r) => ({ valor: r.id, texto: r.nombre }))} />
                    <SelectField id="f-tipo" label="Tipo" value={filtros.tipo} onChange={fijar('tipo')} placeholder="Todos" options={TIPOS} />
                    <SelectField id="f-sistema" label="Sistema" value={filtros.sistema} onChange={fijar('sistema')} placeholder="Todos" options={sistemas} />
                    <SelectField id="f-severidad" label="Severidad" value={filtros.severidad} onChange={fijar('severidad')} placeholder="Todas" options={opciones(SEVERIDADES)} />
                    <SelectField id="f-estado" label="Estado" value={filtros.estado} onChange={fijar('estado')} placeholder="Todos" options={opciones(ESTADOS_FALLA)} />
                </div>}
            </Tarjeta>
            {data && <TotalesEsfuerzo registros={visibles} />}
            {isPending && <Spinner pantalla />}
            {error && <ErrorState mensaje={error.message} onReintentar={refetch} />}
            {data && !data.length && <EmptyState icono={Filter} titulo="No hay fallas con estos filtros" />}
            {data?.length > 0 && (
                <ul className="flex flex-col gap-4">
                    {data.map((f) => <FallaCard key={`${f.id}-${f.nota_resolucion}`} falla={f} editable={puede(PERMISOS.gestionarFallas)} />)}
                </ul>
            )}
            <ComentariosLista rondaId={filtros.ronda} sistema={filtros.sistema} editable={puede(PERMISOS.gestionarFallas)} />
        </>
    );
};

export default Fallas;
