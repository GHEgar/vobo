import { Link } from 'react-router';
import { TextoConEnlaces } from '@/components/TextoConEnlaces';
import { formatearFecha, formatearRelativa } from '@/utils/formato';
import { TONOS_ICONO, horaDe, iconoDeEvento } from '@/utils/actividad';

const capturasTexto = (n) => (n === 1 ? '1 captura' : `${n} capturas`);

const Caso = ({ evento }) => {
    if (!evento.caso_id) return null;
    const partes = [evento.caso_titulo ? `${evento.caso_id} · ${evento.caso_titulo}` : evento.caso_id];
    if (evento.paso) partes.push(`paso ${evento.paso}`);
    if (evento.capturas) partes.push(capturasTexto(evento.capturas));
    return <p className="mt-0.5 wrap-anywhere tipo-media text-xs text-texto-tenue">{partes.join(' · ')}</p>;
};

export const Evento = ({ evento, onNavegar }) => {
    const { icono: Icono, tono } = iconoDeEvento(evento);
    const exacta = formatearFecha(evento.cuando);
    const titulo = evento.aproximado ? `${exacta} (hora del último guardado del caso)` : exacta;
    return (
        <li className="flex items-start gap-3 py-2.5">
            <span aria-hidden="true" className={`flex h-[32px] w-[32px] shrink-0 items-center justify-center rounded-full ${TONOS_ICONO[tono]}`}>
                <Icono size={17} />
            </span>
            <div className="min-w-0 flex-1">
                <p className="wrap-anywhere text-sm text-texto">
                    <span className="tipo-negrita">{evento.usuario.nombre}</span>
                    {' '}
                    <span className="tipo-media text-texto-tenue">{evento.resumen}</span>
                </p>
                <Caso evento={evento} />
                {evento.comentario && (
                    <p className="mt-1 line-clamp-3 wrap-anywhere rounded-xl bg-fondo px-3 py-1.5 tipo-media text-xs text-texto-tenue"><TextoConEnlaces texto={evento.comentario} /></p>
                )}
                <p className="mt-0.5 tipo-media text-[11px] text-texto-apagado">
                    <time dateTime={evento.cuando} title={titulo}>{horaDe(evento.cuando)} · {formatearRelativa(evento.cuando)}</time>
                </p>
            </div>
            {evento.ruta && (
                <Link to={evento.ruta} onClick={onNavegar} className="shrink-0 self-center tipo-negrita text-xs text-primario hover:underline">
                    Ver
                </Link>
            )}
        </li>
    );
};
