import { useState } from 'react';
import { Button } from '@/components/Button';
import { Chip } from '@/components/Chip';
import { TextField } from '@/components/Field';
import { Label } from '@/components/Label';
import { formatearDia, vencido } from '@/utils/seguimiento';

const COMPLETA = /^\d{4}-\d{2}-\d{2}$/;

export const PlazoCampo = ({ id, plazo, responsable, resuelto, editable, onCambiar, textoVencido = 'Vencida' }) => {
    const [borrador, setBorrador] = useState(null);
    const valor = borrador ?? plazo ?? '';
    const atrasado = vencido(plazo, resuelto);
    const cambiar = (e) => {
        const nuevo = e.target.value;
        setBorrador(nuevo);
        if (COMPLETA.test(nuevo) && nuevo !== plazo) onCambiar(nuevo);
    };
    const quitar = () => {
        setBorrador(null);
        onCambiar(null);
    };

    return (
        <div className="min-w-0">
            {editable ? (
                <div className="w-full sm:w-[190px] [&>div]:mt-0">
                    <TextField id={`plazo-${id}`} label="Plazo" tooltip="Fecha compromiso. Quien la fija queda como responsable." type="date" value={valor} onChange={cambiar} onBlur={() => setBorrador(null)} />
                </div>
            ) : (
                <>
                    <Label as="p" text="Plazo" />
                    <p className={`mt-3 tipo-negrita text-sm ${plazo ? 'text-texto' : 'text-texto-apagado'}`}>{plazo ? formatearDia(plazo) : 'Sin plazo'}</p>
                </>
            )}
            {plazo && (
                <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1">
                    {atrasado && <Chip tono="error">{textoVencido}</Chip>}
                    {responsable && <p className="tipo-media text-xs text-texto-tenue">Responsable: {responsable}</p>}
                    {editable && <Button label="Quitar plazo" variant="link" small className="px-0" onClick={quitar} />}
                </div>
            )}
        </div>
    );
};
