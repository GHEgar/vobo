import { useEffect, useRef, useState } from 'react';
import { TextField } from '@/components/Field';
import { Label } from '@/components/Label';
import { AYUDA_ESFUERZO, formatearEsfuerzo } from '@/utils/seguimiento';

const MAXIMO = 1000;

const leer = (texto) => {
    const limpio = String(texto).trim().replace(',', '.');
    if (!limpio) return null;
    const valor = Number(limpio);
    return Number.isNaN(valor) || valor < 0 || valor > MAXIMO ? undefined : valor;
};

export const EsfuerzoCampo = ({ id, horas, editable, onCambiar }) => {
    const [borrador, setBorrador] = useState(null);
    const pendiente = useRef(null);
    const valor = borrador ?? horas ?? '';
    const legible = formatearEsfuerzo(horas);

    const guardar = () => {
        if (borrador === null) return;
        setBorrador(null);
        const nuevo = leer(borrador);
        if (nuevo !== undefined && nuevo !== (horas ?? null)) onCambiar(nuevo);
    };

    useEffect(() => {
        pendiente.current = guardar;
    });
    useEffect(() => () => pendiente.current?.(), []);

    if (!editable) {
        return (
            <div className="min-w-0">
                <Label as="p" text="Esfuerzo" />
                <p className={`mt-3 tipo-negrita text-sm ${legible ? 'text-texto' : 'text-texto-apagado'}`}>{legible || 'Sin estimar'}</p>
            </div>
        );
    }
    return (
        <div className="min-w-0">
            <div className="w-full sm:w-[190px] [&>div]:mt-0">
                <TextField
                    id={`esfuerzo-${id}`}
                    label="Esfuerzo (horas)"
                    tooltip="Horas de trabajo estimadas para resolverlo. Quien lo fija queda como responsable."
                    type="number"
                    inputMode="decimal"
                    min={0}
                    max={MAXIMO}
                    step={0.5}
                    placeholder="Sin estimar"
                    value={valor}
                    onChange={(e) => setBorrador(e.target.value)}
                    onBlur={guardar}
                    onKeyDown={(e) => {
                        if (e.key !== 'Enter') return;
                        e.preventDefault();
                        guardar();
                    }}
                />
            </div>
            <p className="mt-2 tipo-media text-xs text-texto-tenue">{AYUDA_ESFUERZO}{legible && horas >= 8 ? ` · ${legible}` : ''}</p>
        </div>
    );
};
