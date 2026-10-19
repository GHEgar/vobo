import { useState } from 'react';
import { Button } from '@/components/Button';
import { TextField } from '@/components/Field';

export const NotaResolucion = ({ id, nota, editable, guardando, onGuardar }) => {
    const [editando, setEditando] = useState(false);
    const [borrador, setBorrador] = useState(nota);
    const abrir = () => {
        setBorrador(nota);
        setEditando(true);
        requestAnimationFrame(() => document.getElementById(`nota-${id}`)?.focus());
    };
    const guardar = (e) => {
        e.preventDefault();
        onGuardar(borrador.trim(), () => setEditando(false));
    };

    if (editando) {
        return (
            <form onSubmit={guardar} className="mt-3 flex flex-col gap-2">
                <TextField id={`nota-${id}`} label="Nota de resolución" tooltip="Qué se corrigió y en qué versión, para quien revalide." multiline rows={2} maxLength={4000} value={borrador} onChange={(e) => setBorrador(e.target.value)} />
                <div className="flex flex-wrap justify-end gap-2">
                    <Button label="Cancelar" variant="secondary" small onClick={() => setEditando(false)} />
                    <Button type="submit" label="Guardar nota" variant="outline" small disabled={borrador.trim() === nota} loading={guardando} />
                </div>
            </form>
        );
    }
    if (!nota) return editable ? <div className="mt-3"><Button label="Agregar nota" variant="ghost" small onClick={abrir} /></div> : null;
    return (
        <div className="mt-3 rounded-xl bg-pasa-fondo px-4 py-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="tipo-negrita text-xs text-pasa">Nota de resolución</p>
                {editable && <Button label="Editar nota" variant="link" small className="px-0" onClick={abrir} />}
            </div>
            <p className="mt-1 whitespace-pre-line wrap-anywhere tipo-regular text-sm text-texto">{nota}</p>
        </div>
    );
};
