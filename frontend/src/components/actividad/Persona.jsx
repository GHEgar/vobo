import { Link } from 'react-router';
import { useRuta } from '@/hooks/useProyecto';
import { iniciales } from '@/utils/formato';
import { describirPresencia, enlacePresencia, haceTiempo } from '@/utils/presencia';
import { DISPOSITIVOS, duracion, pantallaLegible } from '@/utils/actividad';

const PUNTO = {
    activo: { clase: 'bg-exito', texto: 'Activo' },
    inactivo: { clase: 'bg-texto-apagado', texto: 'Inactivo' },
};

const Detalles = ({ persona, ronda }) => {
    const dispositivo = DISPOSITIVOS[persona.dispositivo] ?? DISPOSITIVOS.escritorio;
    const Icono = dispositivo.icono;
    const pantalla = pantallaLegible(persona.pantalla);
    return (
        <ul className="mt-2 flex flex-wrap gap-x-3 gap-y-1 tipo-media text-[11px] text-texto-apagado">
            {persona.sesion_segundos > 0 && <li>En sesión desde hace {duracion(persona.sesion_segundos)}</li>}
            {ronda && <li>{ronda}</li>}
            <li className="inline-flex items-center gap-1">
                <Icono size={13} className="shrink-0" aria-hidden="true" />
                <span>{[persona.navegador, dispositivo.texto, pantalla].filter(Boolean).join(' · ')}</span>
            </li>
        </ul>
    );
};

export const Persona = ({ persona, ronda, detallada = false, onNavegar }) => {
    const ruta = useRuta();
    const punto = PUNTO[persona.estado];
    const enlace = enlacePresencia(persona, ruta);
    return (
        <li className="flex items-start gap-3 rounded-2xl bg-fondo p-3">
            <span className="relative flex h-[36px] w-[36px] shrink-0 items-center justify-center rounded-full bg-primario-claro tipo-negrita text-sm text-primario" aria-hidden="true">
                {iniciales(persona.nombre)}
                <span className={`absolute -right-0.5 -bottom-0.5 h-[12px] w-[12px] rounded-full ring-2 ring-white ${punto.clase}`} />
            </span>
            <div className="min-w-0 flex-1">
                <p className="flex flex-wrap items-baseline gap-x-2 tipo-negrita text-sm text-texto">
                    <span>{persona.nombre}{persona.yo && <span className="tipo-media text-texto-apagado"> (tú)</span>}</span>
                    <span className="tipo-media text-[11px] text-texto-apagado">
                        <span className="sr-only">{punto.texto}, </span>{haceTiempo(persona.hace_segundos)}
                    </span>
                </p>
                <p className="mt-0.5 break-words tipo-media text-xs text-texto-tenue">{describirPresencia(persona)}</p>
                {detallada && <Detalles persona={persona} ronda={ronda} />}
            </div>
            {enlace && (
                <Link to={enlace} onClick={onNavegar} className="shrink-0 self-center tipo-negrita text-xs text-primario hover:underline">
                    Ver caso
                </Link>
            )}
        </li>
    );
};
