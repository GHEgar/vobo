import { Check, Close } from 'tesela/react';
import { Tarjeta } from '@/components/Tarjeta';

export const Veredicto = ({ tablero }) => {
    const sale = tablero.veredicto === 'Sale';
    return (
        <Tarjeta className={sale ? 'ring-1 ring-pasa-borde' : 'ring-1 ring-falla-borde'}>
            <p className="tipo-media text-xs text-texto-apagado">Criterios de salida</p>
            <p className={`tipo-negrita text-3xl ${sale ? 'text-pasa' : 'text-falla'}`}>{tablero.veredicto}</p>
            <ul className="mt-4 flex flex-col gap-2">
                {tablero.criterios.map((c) => (
                    <li key={c.clave} className="flex items-start gap-3">
                        <span aria-hidden="true" className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full ${c.cumple ? 'bg-pasa-fondo text-pasa' : 'bg-falla-fondo text-falla'}`}>
                            {c.cumple ? <Check size={12} stroke={2.5} /> : <Close size={12} stroke={2.5} />}
                        </span>
                        <span className="flex flex-col">
                            <span className="tipo-negrita text-sm text-texto">
                                <span className="sr-only">{c.cumple ? 'Cumple: ' : 'No cumple: '}</span>
                                {c.descripcion}
                            </span>
                            <span className="tipo-media text-xs text-texto-tenue">{c.detalle}</span>
                        </span>
                    </li>
                ))}
            </ul>
        </Tarjeta>
    );
};
