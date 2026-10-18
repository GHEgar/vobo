import { useReloj } from '@/hooks/usePantalla';
import { PALETA } from '@/utils/pantalla/paleta';
import { haceCuanto } from '@/utils/pantalla/formato';

const Punto = ({ color, tam }) => <span aria-hidden="true" className="inline-block shrink-0 rounded-full" style={{ width: tam, height: tam, background: color }} />;

const Evento = ({ evento, ahora }) => (
    <span className="inline-flex items-center gap-3.5" style={{ fontSize: 26 }}>
        <Punto color={evento.color} tam={14} />
        <span style={{ fontFamily: 'var(--tipo-negrita)', fontWeight: 600 }}>{evento.quien}</span>
        <span style={{ color: PALETA.medio }}>{evento.texto}</span>
        <span style={{ color: PALETA.apagado }}>{haceCuanto(evento.cuando, ahora)}</span>
    </span>
);

export const Cinta = ({ eventos }) => {
    const ahora = useReloj(30 * 1000).getTime();
    const duracion = Math.max(30, eventos.length * 7);
    return (
        <footer className="flex shrink-0 items-center gap-7 px-[72px] pb-10">
            <span className="shrink-0" style={{ fontSize: 24, color: PALETA.tenue }}>Ahora</span>
            <div className="flex h-[76px] grow items-center overflow-hidden rounded-full" style={{ background: PALETA.tarjeta }}>
                {eventos.length === 0 && <span className="pl-8" style={{ fontSize: 24, color: PALETA.apagado }}>Sin movimientos recientes</span>}
                {eventos.length > 0 && (
                    <div className="pantalla-cinta flex gap-12 whitespace-nowrap pl-8" style={{ animationDuration: `${duracion}s` }} aria-live="off">
                        {[...eventos, ...eventos].map((e, i) => <Evento key={`${e.id}-${i}`} evento={e} ahora={ahora} />)}
                    </div>
                )}
            </div>
        </footer>
    );
};
