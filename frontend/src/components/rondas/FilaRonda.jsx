import { useState } from 'react';
import { Button } from '@/components/Button';
import { Chip } from '@/components/Chip';
import { TextField } from '@/components/Field';
import { Modal } from '@/components/Modal';
import { useActualizarRonda, useBorrarRonda } from '@/hooks/useValidacion';
import { formatearFecha } from '@/utils/formato';

const Renombrar = ({ ronda, onListo }) => {
    const actualizar = useActualizarRonda();
    const [nombre, setNombre] = useState(ronda.nombre);

    const guardar = async (e) => {
        e.preventDefault();
        await actualizar.mutateAsync({ id: ronda.id, nombre: nombre.trim() });
        onListo();
    };

    return (
        <form onSubmit={guardar} className="flex grow flex-wrap items-end gap-2">
            <div className="grow">
                <TextField id={`ronda-${ronda.id}-nombre`} label="Nombre de la ronda" value={nombre} onChange={(e) => setNombre(e.target.value)} />
            </div>
            <Button small type="submit" label="Guardar" disabled={!nombre.trim()} loading={actualizar.isPending} />
            <Button small variant="link" label="Cancelar" onClick={onListo} />
            {actualizar.error && <p className="w-full tipo-media text-xs text-error-fuerte">{actualizar.error.message}</p>}
        </form>
    );
};

const ConfirmarBorrado = ({ ronda, abierto, onCerrar }) => {
    const borrar = useBorrarRonda();

    const confirmar = async () => {
        await borrar.mutateAsync(ronda.id);
        onCerrar();
    };

    return (
        <Modal abierto={abierto} titulo={`Borrar ${ronda.nombre}`} onCerrar={onCerrar} ancho="max-w-md">
            <p className="tipo-media text-sm text-texto-tenue">
                Se borran sus asignaciones, resultados, comentarios, fallas, evidencias y decisiones. No se puede deshacer.
            </p>
            {borrar.error && <p className="mt-3 tipo-media text-xs text-error-fuerte">{borrar.error.message}</p>}
            <div className="mt-5 flex justify-end gap-2">
                <Button variant="secondary" label="Cancelar" onClick={onCerrar} />
                <Button variant="danger" label="Borrar ronda" loading={borrar.isPending} onClick={confirmar} />
            </div>
        </Modal>
    );
};

export const FilaRonda = ({ ronda }) => {
    const actualizar = useActualizarRonda();
    const [editando, setEditando] = useState(false);
    const [borrando, setBorrando] = useState(false);

    return (
        <li className="flex flex-wrap items-center justify-between gap-3 rounded-2xl bg-fondo px-5 py-3">
            {editando ? (
                <Renombrar ronda={ronda} onListo={() => setEditando(false)} />
            ) : (
                <>
                    <span className="flex flex-col">
                        <span className="tipo-negrita text-sm text-texto">{ronda.nombre}</span>
                        <span className="tipo-media text-xs text-texto-apagado">{ronda.snapshot || 'sin snapshot'} · {formatearFecha(ronda.creada)}</span>
                    </span>
                    <span className="flex flex-wrap items-center gap-2">
                        <Chip tono={ronda.abierta ? 'exito' : 'neutro'}>{ronda.abierta ? 'Abierta' : 'Cerrada'}</Chip>
                        <Button small variant="secondary" label={ronda.abierta ? 'Cerrar' : 'Reabrir'} onClick={() => actualizar.mutate({ id: ronda.id, abierta: !ronda.abierta })} />
                        <Button small variant="outline" label="Renombrar" onClick={() => setEditando(true)} />
                        <Button small variant="danger" label="Borrar" onClick={() => setBorrando(true)} />
                    </span>
                </>
            )}
            <ConfirmarBorrado ronda={ronda} abierto={borrando} onCerrar={() => setBorrando(false)} />
        </li>
    );
};
