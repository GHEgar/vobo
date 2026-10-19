import { History } from 'tesela/react';
import { AYUDA_ESFUERZO, formatearEsfuerzo, sumarEsfuerzo } from '@/utils/seguimiento';

const Cifra = ({ termino, children }) => (
    <span className="inline-flex items-baseline gap-1.5">
        <span className="tipo-media text-texto-tenue">{termino}</span>
        <span className="tipo-negrita text-texto">{children}</span>
    </span>
);

export const TotalesEsfuerzo = ({ registros }) => {
    if (!registros.length) return null;
    const suma = sumarEsfuerzo(registros);
    const seguidores = registros.filter((r) => r.principal).length;
    return (
        <p aria-label="Esfuerzo estimado de lo visible" className="flex flex-wrap items-center gap-x-5 gap-y-1 rounded-2xl bg-white px-5 py-3 text-[13px] shadow-[0px_3px_12px_var(--color-sombra-tenue)]">
            <History size={16} className="shrink-0 text-primario" />
            <Cifra termino="Esfuerzo total">{formatearEsfuerzo(suma.total) || '0 h'}</Cifra>
            <Cifra termino="Pendiente">{formatearEsfuerzo(suma.pendiente) || '0 h'}</Cifra>
            {suma.sinEstimar > 0 && <Cifra termino="Sin estimar">{suma.sinEstimar}</Cifra>}
            {seguidores > 0 && <Cifra termino="Siguen a otro, no cuentan">{seguidores}</Cifra>}
            <span className="tipo-media text-xs text-texto-apagado sm:ml-auto">{AYUDA_ESFUERZO}</span>
        </p>
    );
};
