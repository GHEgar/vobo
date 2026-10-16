import { Close, Help, Upload } from 'tesela/react';

const Circulo = ({ className, fondo, children }) => (
    <span aria-hidden="true" className={`inline-flex shrink-0 items-center justify-center rounded-full ${fondo} ${className}`}>
        {children}
    </span>
);

export const IconoTooltip = ({ className = '' }) => (
    <Help size={20} className={`shrink-0 text-aviso ${className}`} />
);

export const IconoCerrar = ({ className = '' }) => (
    <Circulo className={className} fondo="bg-fondo text-neutro-icono">
        <Close size={14} stroke={2} />
    </Circulo>
);

export const IconoSubir = ({ className = '' }) => (
    <Circulo className={className} fondo="bg-primario-suave text-primario">
        <Upload size={26} />
    </Circulo>
);

export const IconoVacio = ({ icono: Icono }) => (
    <span aria-hidden="true" className="mb-1 inline-flex h-[64px] w-[64px] items-center justify-center rounded-full bg-primario-suave text-primario">
        <Icono size={40} variant="duotone" />
    </span>
);
