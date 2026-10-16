import { useState } from 'react';
import { Button } from '@/components/Button';
import { BotonMas } from '@/components/BotonMas';
import { Chip } from '@/components/Chip';
import { Modal } from '@/components/Modal';
import { NombreProyecto } from '@/components/NombreProyecto';
import { Spinner } from '@/components/Spinner';
import { ErrorState } from '@/components/Estados';
import { Titulo } from '@/components/Tarjeta';
import { ControlesOrden } from '@/components/editor/ListaOrdenable';
import { EditorProyecto } from '@/components/admin/EditorProyecto';
import { useActualizarProyecto, useBorrarProyecto, useOrdenarProyectos, useProyectosAdmin } from '@/hooks/useAdmin';
import { mover } from '@/utils/editor';

const plural = (n, uno, varios) => `${n} ${n === 1 ? uno : varios}`;

const Acciones = ({ proyecto, onEditar }) => {
    const actualizar = useActualizarProyecto();
    const borrar = useBorrarProyecto();
    const [confirmando, setConfirmando] = useState(false);
    const borrable = !proyecto.por_omision && proyecto.rondas === 0;
    const error = actualizar.error ?? borrar.error;

    return (
        <div className="flex min-w-0 flex-col items-start gap-2 lg:items-end">
            <div className="flex flex-wrap items-center gap-2">
                <Button label="Editar" small variant="ghost" onClick={onEditar} />
                {!proyecto.por_omision && !proyecto.archivado && (
                    <Button label="Marcar por omisión" small variant="ghost" loading={actualizar.isPending} onClick={() => actualizar.mutate({ id: proyecto.id, por_omision: true })} />
                )}
                {!proyecto.por_omision && (
                    <Button label={proyecto.archivado ? 'Desarchivar' : 'Archivar'} small variant="ghost" onClick={() => actualizar.mutate({ id: proyecto.id, archivado: !proyecto.archivado })} />
                )}
                {borrable && !confirmando && <Button label="Borrar" small variant="enlaceRojo" onClick={() => setConfirmando(true)} />}
                {confirmando && (
                    <>
                        <Button label="Borrar con su contenido" small variant="danger" loading={borrar.isPending} onClick={() => borrar.mutate(proyecto.id)} />
                        <Button label="Cancelar" small variant="link" onClick={() => setConfirmando(false)} />
                    </>
                )}
            </div>
            {error && <p role="alert" className="tipo-media text-xs text-error-fuerte">{error.message}</p>}
        </div>
    );
};

const FilaProyecto = ({ proyecto, indice, total, multiples, onMover, onEditar }) => (
    <li className="flex flex-col gap-3 rounded-2xl bg-fondo px-4 py-3 lg:flex-row lg:items-start lg:justify-between">
        <div className="flex min-w-0 flex-1 flex-col gap-2">
            <div className="flex min-w-0 flex-wrap items-baseline gap-x-2">
                <NombreProyecto nombre={proyecto.nombre} color={proyecto.color_nombre} className="max-w-full" />
                <span className="tipo-media text-[11px] text-texto-apagado">{proyecto.clave}</span>
            </div>
            {proyecto.descripcion && <p className="tipo-media text-xs text-texto-tenue">{proyecto.descripcion}</p>}
            <div className="flex flex-wrap gap-2">
                {proyecto.por_omision && <Chip tono="marca">Por omisión</Chip>}
                {proyecto.archivado && <Chip tono="aviso">Archivado</Chip>}
                <Chip>{plural(proyecto.rondas, 'ronda', 'rondas')}</Chip>
                {multiples && <Chip>{plural(proyecto.secciones, 'sección', 'secciones')}</Chip>}
            </div>
        </div>
        <div className="flex min-w-0 flex-wrap items-start gap-2 lg:shrink-0">
            {multiples && <Acciones proyecto={proyecto} onEditar={onEditar} />}
            {!multiples && <Button label="Editar" small variant="ghost" onClick={onEditar} />}
            {total > 1 && <ControlesOrden indice={indice} total={total} nombre={proyecto.nombre} onMover={onMover} />}
        </div>
    </li>
);

export const Proyectos = () => {
    const estado = useProyectosAdmin();
    const ordenar = useOrdenarProyectos();
    const [editando, setEditando] = useState(null);

    if (estado.isPending) return <Spinner />;
    if (estado.error) return <ErrorState mensaje={estado.error.message} onReintentar={estado.refetch} />;
    const { proyectos, multiples, motivo } = estado.data;
    const reordenar = (i, delta) => ordenar.mutate(mover(proyectos, i, delta).map((p) => p.id));

    return (
        <>
            <Titulo
                descripcion="Cada proyecto es lo que se valida, con su propio contenido y sus propias rondas. Los sistemas agrupan secciones dentro de cada uno."
                accion={multiples ? <BotonMas etiqueta="Nuevo proyecto" ayuda="Crear un proyecto con su propio contenido y rondas" onClick={() => setEditando({ proyecto: null })} /> : null}
            >
                Proyectos
            </Titulo>
            {!multiples && (
                <p className="mb-4 rounded-2xl bg-pendiente-fondo px-4 py-3 tipo-media text-xs text-pendiente">
                    {motivo}. Con el contenido en la base, cada proyecto tiene sus secciones, casos y procedimientos, que se editan en el editor.
                </p>
            )}
            {ordenar.error && <p role="alert" className="mb-3 tipo-media text-xs text-error-fuerte">{ordenar.error.message}</p>}
            <ul className="flex flex-col gap-2">
                {proyectos.map((p, i) => (
                    <FilaProyecto
                        key={p.id}
                        proyecto={p}
                        indice={i}
                        total={proyectos.length}
                        multiples={multiples}
                        onMover={(delta) => reordenar(i, delta)}
                        onEditar={() => setEditando({ proyecto: p })}
                    />
                ))}
            </ul>
            <Modal abierto={Boolean(editando)} titulo={editando?.proyecto ? `Editar ${editando.proyecto.nombre}` : 'Nuevo proyecto'} onCerrar={() => setEditando(null)} ancho="max-w-lg">
                {editando && <EditorProyecto key={editando.proyecto?.id ?? 'nuevo'} proyecto={editando.proyecto} onListo={() => setEditando(null)} />}
            </Modal>
        </>
    );
};
