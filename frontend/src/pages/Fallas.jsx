import { useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router';
import { SelectField } from '@/components/Field';
import { Spinner } from '@/components/Spinner';
import { EmptyState, ErrorState } from '@/components/Estados';
import { Tarjeta } from '@/components/Tarjeta';
import { ComentariosLista } from '@/components/fallas/ComentariosLista';
import { FallaCard } from '@/components/fallas/FallaCard';
import { useRonda } from '@/hooks/useRonda';
import { useSesion } from '@/hooks/useSesion';
import { PERMISOS } from '@/utils/permisos';
import { useContenido, useFallas } from '@/hooks/useValidacion';
import { consulta as aConsulta } from '@/services/api';
import { urlInformeFallas } from '@/services/validacion';
import { zonaHoraria } from '@/utils/informeFallas';
import { ESTADOS_FALLA, SEVERIDADES, opciones } from '@/utils/etiquetas';

const TIPOS = [
    { valor: 'falla', texto: 'Fallas' },
    { valor: 'no_pude', texto: 'No pude probarlo' },
];

const ENLACE = 'inline-flex h-[30px] items-center rounded-full border border-primario px-4 tipo-negrita text-xs text-primario hover:bg-primario-suave';

const Fallas = () => {
    const { puede } = useSesion();
    const { ronda, rondas } = useRonda();
    const { data: contenido } = useContenido();
    const [params] = useSearchParams();
    const [filtros, setFiltros] = useState(() => ({
        sistema: params.get('sistema') ?? '',
        severidad: params.get('severidad') ?? '',
        estado: '',
        tipo: 'falla',
        ronda: null,
    }));
    const consulta = { ...filtros, ronda: filtros.ronda ?? ronda?.id ?? '' };
    const { data, isPending, error, refetch } = useFallas(consulta);
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
                    <div className="flex flex-wrap gap-2">
                        <a href={urlInformeFallas({ ...consulta, tz: zonaHoraria() })} download className={ENLACE}>Descargar CSV</a>
                        <Link to={`/informe-fallas${aConsulta(consulta)}`} className={ENLACE}>Informe imprimible</Link>
                    </div>
                </div>
                <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
                    <SelectField id="f-ronda" label="Ronda" value={consulta.ronda} onChange={fijar('ronda')} placeholder="Todas" options={rondas.map((r) => ({ valor: r.id, texto: r.nombre }))} />
                    <SelectField id="f-tipo" label="Tipo" value={filtros.tipo} onChange={fijar('tipo')} placeholder="Todos" options={TIPOS} />
                    <SelectField id="f-sistema" label="Sistema" value={filtros.sistema} onChange={fijar('sistema')} placeholder="Todos" options={sistemas} />
                    <SelectField id="f-severidad" label="Severidad" value={filtros.severidad} onChange={fijar('severidad')} placeholder="Todas" options={opciones(SEVERIDADES)} />
                    <SelectField id="f-estado" label="Estado" value={filtros.estado} onChange={fijar('estado')} placeholder="Todos" options={opciones(ESTADOS_FALLA)} />
                </div>
            </Tarjeta>
            {isPending && <Spinner pantalla />}
            {error && <ErrorState mensaje={error.message} onReintentar={refetch} />}
            {data && !data.length && <EmptyState titulo="No hay fallas con estos filtros" />}
            {data?.length > 0 && (
                <ul className="flex flex-col gap-4">
                    {data.map((f) => <FallaCard key={`${f.id}-${f.nota_resolucion}`} falla={f} editable={puede(PERMISOS.gestionarFallas)} />)}
                </ul>
            )}
            <ComentariosLista rondaId={consulta.ronda} sistema={filtros.sistema} />
        </>
    );
};

export default Fallas;
