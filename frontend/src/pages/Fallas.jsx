import { useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router';
import { Checkbox } from '@/components/Checkbox';
import { SelectField } from '@/components/Field';
import { Spinner } from '@/components/Spinner';
import { EmptyState, ErrorState } from '@/components/Estados';
import { Tarjeta } from '@/components/Tarjeta';
import { ComentariosLista } from '@/components/fallas/ComentariosLista';
import { FallaCard } from '@/components/fallas/FallaCard';
import { useRonda } from '@/hooks/useRonda';
import { useClaveProyecto, useRuta } from '@/hooks/useProyecto';
import { useSesion } from '@/hooks/useSesion';
import { useLocalStorageState } from '@/hooks/useLocalStorageState';
import { PERMISOS } from '@/utils/permisos';
import { useContenido, useFallas } from '@/hooks/useValidacion';
import { consulta as aConsulta } from '@/services/api';
import { urlInformeFallas } from '@/services/validacion';
import { CLAVE_COMENTARIOS, zonaHoraria } from '@/utils/informeFallas';
import { ESTADOS_FALLA, SEVERIDADES, opciones } from '@/utils/etiquetas';
import { FileTable, FileText, Filter } from 'tesela/react';

const TIPOS = [
    { valor: 'falla', texto: 'Fallas' },
    { valor: 'no_pude', texto: 'No pude probarlo' },
];

const ENLACE = 'inline-flex h-[30px] items-center gap-1.5 rounded-full border border-primario px-4 tipo-negrita text-xs text-primario hover:bg-primario-suave';

const Fallas = () => {
    const { puede } = useSesion();
    const { ronda, rondas } = useRonda();
    const ruta = useRuta();
    const proyecto = useClaveProyecto();
    const { data: contenido } = useContenido();
    const [params] = useSearchParams();
    const [filtros, setFiltros] = useState(() => ({
        sistema: params.get('sistema') ?? '',
        severidad: params.get('severidad') ?? '',
        estado: '',
        tipo: 'falla',
        ronda: null,
    }));
    const [conComentarios, setConComentarios] = useLocalStorageState(CLAVE_COMENTARIOS, false);
    const consulta = { ...filtros, ronda: filtros.ronda ?? ronda?.id ?? '' };
    const informe = { ...consulta, comentarios: conComentarios ? 1 : '' };
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
                    <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
                        <Checkbox id="f-comentarios" checked={conComentarios} onChange={setConComentarios}>Incluir comentarios</Checkbox>
                        <div className="flex flex-wrap gap-2">
                            <a href={urlInformeFallas({ ...informe, proyecto, tz: zonaHoraria() })} download className={ENLACE}><FileTable size={16} className="shrink-0" />Descargar CSV</a>
                            <Link to={ruta(`/informe-fallas${aConsulta(informe)}`)} title="Informe imprimible o PDF" className={ENLACE}><FileText size={16} className="shrink-0" />Informe</Link>
                        </div>
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
            {data && !data.length && <EmptyState icono={Filter} titulo="No hay fallas con estos filtros" />}
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
