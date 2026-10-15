import { Close, Info, Upload } from 'tesela/react';

const Circulo = ({ className, fondo, children }) => (
    <span aria-hidden="true" className={`inline-flex shrink-0 items-center justify-center rounded-full ${fondo} ${className}`}>
        {children}
    </span>
);

export const IconoTooltip = ({ className = '' }) => (
    <Info size={20} stroke={1.75} className={`shrink-0 text-aviso ${className}`} />
);

export const IconoCerrar = ({ className = '' }) => (
    <Circulo className={className} fondo="bg-fondo text-neutro-icono">
        <Close size={14} stroke={2} />
    </Circulo>
);

export const IconoSubir = ({ className = '' }) => (
    <Circulo className={className} fondo="bg-primario-suave text-primario">
        <Upload size={26} stroke={1.75} />
    </Circulo>
);
