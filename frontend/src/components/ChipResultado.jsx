import { Alert, CheckCircle, CloseCircle } from 'tesela/react';
import { Chip } from '@/components/Chip';
import { ESTADOS_RESULTADO } from '@/utils/etiquetas';

const ICONOS = { pasa: CheckCircle, falla: CloseCircle, no_pude: Alert };

export const IconoResultado = ({ estado, size = 16, className = '' }) => {
    const Icono = ICONOS[estado];
    return Icono ? <Icono size={size} className={`shrink-0 ${className}`} /> : null;
};

export const ChipResultado = ({ estado, activo }) => (
    <Chip tono={ESTADOS_RESULTADO[estado].tono} activo={activo}>
        <IconoResultado estado={estado} />
        {ESTADOS_RESULTADO[estado].texto}
    </Chip>
);
