import { CheckCircle, CloseCircle } from 'tesela/react';
import { Tarjeta } from '@/components/Tarjeta';

export const Veredicto = ({ tablero }) => {
    const sale = tablero.veredicto === 'Sale';
    return (
        <Tarjeta className={sale ? 'ring-1 ring-pasa-borde' : 'ring-1 ring-falla-borde'}>
            <p className="tipo-media text-xs text-texto-apagado">Criterios de salida</p>
            <p className={`flex items-center gap-2 tipo-negrita text-3xl ${sale ? 'text-pasa' : 'text-falla'}`}>
                {sale ? <CheckCircle size={32} className="shrink-0" /> : <CloseCircle size={32} className="shrink-0" />}
                {tablero.veredicto}
            </p>
            <ul className="mt-4 flex flex-col gap-2">
                {tablero.criterios.map((c) => (
                    <li key={c.clave} className="flex items-start gap-3">
                        {c.cumple
                            ? <CheckCircle size={20} className="shrink-0 text-pasa" />
                            : <CloseCircle size={20} className="shrink-0 text-falla" />}
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
