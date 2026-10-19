import { useEffect, useMemo, useRef, useState } from 'react';
import { Tequio } from '@npmegar/tequio/react';
import { Button } from '@/components/Button';
import { EmptyState, ErrorState } from '@/components/Estados';
import { SelectorRonda } from '@/components/SelectorRonda';
import { Spinner } from '@/components/Spinner';
import { useParticipacion } from '@/hooks/useInformeFallas';
import { useLocalStorageState } from '@/hooks/useLocalStorageState';
import { useProyecto } from '@/hooks/useProyecto';
import { useRonda } from '@/hooks/useRonda';
import { ETIQUETAS } from '@/utils/participacion';
import { Expand, Opacity, Play, Refresh, ShareNodes } from 'tesela/react';

const REFRESCO = 30 * 1000;
const RECORRIDO = { idle: 8000, interval: 15000 };
const AGRUPACIONES = [
    { valor: 'proyecto', texto: 'Proyecto', centro: 'los proyectos' },
    { valor: 'sistema', texto: 'Sistema', centro: 'los sistemas' },
    { valor: 'seccion', texto: 'Sección', centro: 'las secciones' },
];

const usePantallaCompleta = (ref) => {
    const [activa, setActiva] = useState(false);
    useEffect(() => {
        const sincronizar = () => setActiva(document.fullscreenElement === ref.current);
        document.addEventListener('fullscreenchange', sincronizar);
        return () => document.removeEventListener('fullscreenchange', sincronizar);
    }, [ref]);
    const alternar = () => {
        if (document.fullscreenElement) void document.exitFullscreen();
        else void ref.current?.requestFullscreen();
    };
    return [activa, alternar];
};

const Participacion = () => {
    const { proyectos, clave } = useProyecto();
    const { ronda } = useRonda();
    const activos = useMemo(() => proyectos.filter((p) => !p.archivado), [proyectos]);
    const [ocultos, setOcultos] = useLocalStorageState('validacion.participacion.ocultos', []);
    const [recorrido, setRecorrido] = useLocalStorageState('validacion.participacion.recorrido', false);
    const [oscuro, setOscuro] = useLocalStorageState('validacion.participacion.oscuro', false);
    const [agrupar, setAgrupar] = useLocalStorageState('validacion.participacion.agrupar', 'sistema');
    const [animacion, setAnimacion] = useLocalStorageState('validacion.participacion.animacion', true);
    const grupo = AGRUPACIONES.find((a) => a.valor === agrupar) ?? AGRUPACIONES[1];
    const escenario = useRef(null);
    const [completa, alternarCompleta] = usePantallaCompleta(escenario);

    const claves = activos.map((p) => p.clave).filter((c) => !ocultos.includes(c));
    const unico = claves.length === 1 && claves[0] === clave ? ronda?.id : undefined;
    const { data, isPending, error, refetch } = useParticipacion(claves, unico, true, REFRESCO, grupo.valor);
    const alternarProyecto = (c) => setOcultos(ocultos.includes(c) ? ocultos.filter((x) => x !== c) : [...ocultos, c]);
    const tema = oscuro || completa ? 'dark' : 'light';

    return (
        <>
            <div className="flex flex-wrap items-center gap-2">
                {activos.length > 1 && activos.map((p) => (
                    <Button
                        key={p.clave}
                        small
                        variant={ocultos.includes(p.clave) ? 'secondary' : 'primary'}
                        pressed={!ocultos.includes(p.clave)}
                        disabled={!ocultos.includes(p.clave) && claves.length === 1}
                        label={p.nombre}
                        onClick={() => alternarProyecto(p.clave)}
                    />
                ))}
                {claves.length === 1 && claves[0] === clave && <SelectorRonda />}
                <div role="group" aria-label="Agrupar por" className="flex gap-1">
                    {AGRUPACIONES.map((a) => (
                        <Button key={a.valor} small variant={a.valor === grupo.valor ? 'primary' : 'secondary'} pressed={a.valor === grupo.valor} label={a.texto} onClick={() => setAgrupar(a.valor)} />
                    ))}
                </div>
                <div className="ml-auto flex flex-wrap gap-2">
                    <Button small variant="secondary" pressed={animacion} icono={<Refresh size={14} />} label="Animación" onClick={() => setAnimacion(!animacion)} />
                    <Button small variant="secondary" pressed={recorrido} icono={<Play size={14} />} label="Recorrido" onClick={() => setRecorrido(!recorrido)} />
                    <Button small variant="secondary" pressed={oscuro} icono={<Opacity size={14} />} label={oscuro ? 'Oscuro' : 'Claro'} onClick={() => setOscuro(!oscuro)} />
                    <Button small variant="secondary" icono={<Expand size={14} />} label="Pantalla completa" onClick={alternarCompleta} />
                </div>
            </div>
            <p className="tipo-media text-xs text-texto-apagado">
                Al centro, {grupo.centro} con el anillo de estados de sus casos; alrededor, cada persona con sus casos marcados. Haz clic en un nodo para ver su detalle. Se actualiza cada 30 segundos.
            </p>
            {claves.length === 0 && <EmptyState icono={ShareNodes} titulo="Sin proyectos activos" />}
            {claves.length > 0 && isPending && <Spinner pantalla />}
            {error && <ErrorState mensaje={error.message} onReintentar={refetch} />}
            {data && data.people.length === 0 && (
                <EmptyState icono={ShareNodes} titulo="Nadie ha marcado casos todavía" descripcion="El grafo aparece en cuanto alguien marque su primer caso." />
            )}
            {data && data.people.length > 0 && (
                <div
                    ref={escenario}
                    className={`relative w-full overflow-hidden ${completa ? 'h-dvh bg-[#0d0d0d]' : 'aspect-video rounded-2xl bg-white shadow-[0px_3px_12px_var(--color-sombra-suave)]'}`}
                >
                    <Tequio data={data} theme={tema} locale="es" labels={ETIQUETAS} animated={animacion ? 'always' : false} tour={recorrido || completa ? RECORRIDO : false} table />
                </div>
            )}
        </>
    );
};

export default Participacion;
