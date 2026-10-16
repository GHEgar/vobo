import { Alert, Refresh } from 'tesela/react';
import { Button } from '@/components/Button';
import { IconoVacio } from '@/components/Iconos';

export const EmptyState = ({ titulo, descripcion, accion, icono }) => (
    <div className="flex flex-col items-center gap-2 rounded-2xl bg-white px-6 py-10 text-center">
        {icono && <IconoVacio icono={icono} />}
        <p className="tipo-negrita text-base text-texto">{titulo}</p>
        {descripcion && <p className="max-w-md tipo-media text-sm text-texto-tenue">{descripcion}</p>}
        {accion}
    </div>
);

export const ErrorState = ({ mensaje, onReintentar, pantalla = false }) => (
    <div className={`flex flex-col items-center justify-center gap-3 px-6 py-10 text-center ${pantalla ? 'min-h-[60dvh]' : 'rounded-2xl bg-white'}`}>
        <Alert size={40} variant="duotone" className="text-error-fuerte" />
        <p className="tipo-negrita text-base text-error-fuerte">No se pudo cargar la información</p>
        {mensaje && <p className="max-w-md tipo-media text-sm text-texto-tenue">{mensaje}</p>}
        {onReintentar && <Button label="Reintentar" icono={<Refresh size={18} />} variant="secondary" onClick={() => onReintentar()} />}
    </div>
);
