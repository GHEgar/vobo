import { BotonCopiar } from '@/components/BotonCopiar';
import { formatearFecha } from '@/utils/formato';

export const EnlaceGenerado = ({ enlace, expira, descripcion }) => (
    <div className="flex flex-col gap-3">
        <p className="tipo-media text-sm text-texto-tenue">{descripcion}</p>
        <div className="flex flex-col gap-2 rounded-2xl bg-fondo px-4 py-3">
            <code className="break-all text-xs text-primario">{enlace}</code>
            <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="tipo-media text-xs text-texto-apagado">Un solo uso; vence el {formatearFecha(expira)}.</span>
                <BotonCopiar texto={enlace} etiqueta="Copiar enlace" descripcion="Copiar el enlace al portapapeles" />
            </div>
        </div>
    </div>
);
