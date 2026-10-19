import { useState } from 'react';
import { Button } from '@/components/Button';
import { TextField } from '@/components/Field';

export const NotaResolucion = ({ id, nota, editando, guardando, onGuardar, onCerrar }) => {
    const [borrador, setBorrador] = useState(nota);
    const guardar = (e) => {
        e.preventDefault();
        onGuardar(borrador.trim(), onCerrar);
    };

    if (editando) {
        return (
            <form onSubmit={guardar} className="mt-3 flex flex-col gap-2">
                <TextField id={`nota-${id}`} label="Nota de resolución" tooltip="Qué se corrigió y en qué versión, para quien revalide." multiline rows={2} maxLength={4000} value={borrador} onChange={(e) => setBorrador(e.target.value)} />
                <div className="flex flex-wrap justify-end gap-2">
                    <Button label="Cancelar" variant="secondary" small onClick={onCerrar} />
                    <Button type="submit" label="Guardar nota" variant="outline" small disabled={borrador.trim() === nota} loading={guardando} />
                </div>
            </form>
        );
    }
    if (!nota) return null;
    return (
        <div className="mt-3 rounded-xl bg-pasa-fondo px-4 py-3">
            <p className="tipo-negrita text-xs text-pasa">Nota de resolución</p>
            <p className="mt-1 whitespace-pre-line wrap-anywhere tipo-regular text-sm text-texto">{nota}</p>
        </div>
    );
};
