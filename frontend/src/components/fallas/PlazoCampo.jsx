import { useState } from 'react';
import { Button } from '@/components/Button';
import { Chip } from '@/components/Chip';
import { TextField } from '@/components/Field';
import { formatearDia, vencido } from '@/utils/seguimiento';

const COMPLETA = /^\d{4}-\d{2}-\d{2}$/;

export const PlazoCampo = ({ id, plazo, responsable, resuelto, editable, onCambiar, textoVencido = 'Vencida' }) => {
    const [borrador, setBorrador] = useState(null);
    const valor = borrador ?? plazo ?? '';
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
        <div className="flex flex-wrap items-end gap-x-3 gap-y-2">
            {editable ? (
                <div className="w-[190px]">
                    <TextField id={`plazo-${id}`} label="Plazo" tooltip="Fecha compromiso. Quien la fija queda como responsable." type="date" value={valor} onChange={cambiar} onBlur={() => setBorrador(null)} />
                </div>
            ) : (
                plazo && <p className="tipo-media text-sm text-texto"><span className="text-texto-apagado">Plazo:</span> {formatearDia(plazo)}</p>
            )}
            {editable && plazo && <Button label="Quitar plazo" variant="link" small onClick={quitar} />}
            {plazo && responsable && <p className="pb-2 tipo-media text-xs text-texto-tenue">Responsable: {responsable}</p>}
            {vencido(plazo, resuelto) && <span className="pb-1"><Chip tono="error">{textoVencido}</Chip></span>}
        </div>
    );
};
