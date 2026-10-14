import { useState } from 'react';
import { Button } from '@/components/Button';
import { TextField } from '@/components/Field';

export const ComentarioPaso = ({ id, label, inicial = '', requerido = false, filas = 1, accion, onGuardar, onCancelar, guardando }) => {
    const [texto, setTexto] = useState(inicial ?? '');
    const valido = !requerido || texto.trim().length > 0;
    return (
        <form
            onSubmit={(e) => {
                e.preventDefault();
                if (valido) onGuardar(texto.trim() || null);
            }}
            className="flex flex-col"
        >
            <TextField id={id} label={label} multiline rows={filas} maxLength={1000} value={texto} onChange={(e) => setTexto(e.target.value)} />
            <div className="mt-4 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
                <Button label="Cancelar" variant="secondary" onClick={onCancelar} />
                <Button label={accion} type="submit" disabled={!valido} loading={guardando} />
            </div>
        </form>
    );
};
