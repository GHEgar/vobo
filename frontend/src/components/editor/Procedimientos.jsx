import { useState } from 'react';
import { Edit, History, Play, Trash } from 'tesela/react';
import { BotonMas } from '@/components/BotonMas';
import { Button } from '@/components/Button';
import { Chip } from '@/components/Chip';
import { MediaImagen } from '@/components/MediaImagen';
import { Modal } from '@/components/Modal';
import { Spinner } from '@/components/Spinner';
import { EmptyState, ErrorState } from '@/components/Estados';
import { Titulo } from '@/components/Tarjeta';
import { FormProcedimiento } from '@/components/editor/FormProcedimiento';
import { Historial } from '@/components/editor/Historial';
import { BotonIcono } from '@/components/editor/ListaOrdenable';
import { SubirAnimacion } from '@/components/editor/SubirAnimacion';
import { useBorrarProcedimiento, useProcedimientosEditor } from '@/hooks/useEditor';

const Fila = ({ procedimiento, onEditar, onHistorial }) => {
    const borrar = useBorrarProcedimiento();
    const [confirmando, setConfirmando] = useState(false);
    const usado = procedimiento.usos.length > 0;

    return (
        <li className="flex flex-col gap-3 rounded-2xl bg-fondo px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex min-w-0 items-center gap-3">
                <div className="h-12 w-20 shrink-0 overflow-hidden rounded-lg bg-white">
                    {procedimiento.media && <MediaImagen url={procedimiento.media.url} alt="" tipo={procedimiento.media.mime} className="h-full w-full object-cover" />}
                </div>
                <div className="min-w-0">
                    <p className="tipo-negrita text-sm text-texto">
                        {procedimiento.datos.titulo || procedimiento.id}
                        <span className="tipo-media text-[11px] text-texto-apagado"> · {procedimiento.id}</span>
                    </p>
                    <div className="mt-1 flex flex-wrap gap-1">
                        {!procedimiento.media && <Chip tono="aviso">Sin animación</Chip>}
                        {usado ? <Chip>Lo usan: {procedimiento.usos.join(', ')}</Chip> : <Chip>Sin usos</Chip>}
                    </div>
                    {borrar.error && <p role="alert" className="mt-1 tipo-media text-xs text-error-fuerte">{borrar.error.message}</p>}
                </div>
            </div>
            <div className="flex shrink-0 items-center gap-1">
                <BotonIcono etiqueta={`Editar ${procedimiento.id}`} onClick={onEditar}><Edit size={16} /></BotonIcono>
                <BotonIcono etiqueta={`Historial de ${procedimiento.id}`} onClick={onHistorial}><History size={16} /></BotonIcono>
                {!confirmando && (
                    <BotonIcono etiqueta={usado ? 'Lo usan secciones: quítalo de ellas primero' : `Borrar ${procedimiento.id}`} peligro disabled={usado} onClick={() => setConfirmando(true)}>
                        <Trash size={16} />
                    </BotonIcono>
                )}
                {confirmando && (
                    <>
                        <Button label="Confirmar borrado" small variant="danger" loading={borrar.isPending} onClick={() => borrar.mutate(procedimiento.id)} />
                        <Button label="Cancelar" small variant="link" onClick={() => setConfirmando(false)} />
                    </>
                )}
            </div>
        </li>
    );
};

export const Procedimientos = () => {
    const lista = useProcedimientosEditor();
    const [editando, setEditando] = useState(null);
    const [historial, setHistorial] = useState(null);

    if (lista.isPending) return <Spinner />;
    if (lista.error) return <ErrorState mensaje={lista.error.message} onReintentar={lista.refetch} />;
    const actual = editando?.id ? lista.data.find((p) => p.id === editando.id) : null;

    return (
        <>
            <Titulo
                descripcion="Pasos reutilizables que los casos enlazan; cada uno puede tener una animación."
                accion={<BotonMas etiqueta="Nuevo procedimiento" ayuda="Crear un procedimiento" onClick={() => setEditando({ id: null })} />}
            >
                Procedimientos
            </Titulo>
            {!lista.data.length && <EmptyState icono={Play} titulo="Todavía no hay procedimientos" />}
            <ul className="flex flex-col gap-2">
                {lista.data.map((p) => <Fila key={p.id} procedimiento={p} onEditar={() => setEditando({ id: p.id })} onHistorial={() => setHistorial(p)} />)}
            </ul>
            <Modal abierto={Boolean(editando)} titulo={actual ? `Editar ${actual.datos.titulo || actual.id}` : 'Nuevo procedimiento'} onCerrar={() => setEditando(null)}>
                {editando && (
                    <>
                        <FormProcedimiento key={`${actual?.id ?? 'nuevo'}-${actual?.actualizado ?? ''}`} procedimiento={actual} onListo={(r) => setEditando({ id: r.id })} />
                        {actual && <SubirAnimacion procedimiento={actual} />}
                    </>
                )}
            </Modal>
            <Historial abierto={Boolean(historial)} tipo="procedimiento" id={historial?.id} titulo={historial?.datos.titulo} onCerrar={() => setHistorial(null)} />
        </>
    );
};
