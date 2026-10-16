import { useState } from 'react';
import { Button } from '@/components/Button';
import { BotonMas } from '@/components/BotonMas';
import { Chip } from '@/components/Chip';
import { Modal } from '@/components/Modal';
import { Spinner } from '@/components/Spinner';
import { ErrorState } from '@/components/Estados';
import { Titulo } from '@/components/Tarjeta';
import { EditorRol } from '@/components/admin/EditorRol';
import { useBorrarRol, usePermisosCatalogo, useRoles } from '@/hooks/useAdmin';

const FilaRol = ({ rol, descripciones, onEditar }) => {
    const borrar = useBorrarRol();
    const [confirmando, setConfirmando] = useState(false);
    const permisos = rol.permisos.includes('validacion.admin') ? ['Todos los permisos'] : rol.permisos.map((p) => descripciones[p] ?? p);

    return (
        <li className="flex flex-col gap-3 rounded-2xl bg-fondo px-4 py-3 lg:flex-row lg:items-start lg:justify-between">
            <div className="flex min-w-0 flex-col gap-2">
                <div>
                    <p className="tipo-negrita text-sm text-texto">
                        {rol.nombre}
                        <span className="tipo-media text-[11px] text-texto-apagado"> · {rol.clave}{rol.sistema ? ' · de sistema' : ''}</span>
                    </p>
                    {rol.descripcion && <p className="tipo-media text-xs text-texto-tenue">{rol.descripcion}</p>}
                </div>
                <div className="flex flex-wrap gap-2">
                    {permisos.map((p) => <Chip key={p} tono="marca">{p}</Chip>)}
                    {!permisos.length && <Chip>Sin permisos</Chip>}
                </div>
                {borrar.error && <p role="alert" className="tipo-media text-xs text-error-fuerte">{borrar.error.message}</p>}
            </div>
            <div className="flex shrink-0 flex-wrap items-center gap-2">
                <Button label="Editar" small variant="ghost" onClick={onEditar} />
                {!rol.sistema && !confirmando && <Button label="Borrar" small variant="enlaceRojo" onClick={() => setConfirmando(true)} />}
                {confirmando && (
                    <>
                        <Button label="Confirmar borrado" small variant="danger" loading={borrar.isPending} onClick={() => borrar.mutate(rol.id)} />
                        <Button label="Cancelar" small variant="link" onClick={() => setConfirmando(false)} />
                    </>
                )}
            </div>
        </li>
    );
};

export const Roles = () => {
    const roles = useRoles();
    const catalogo = usePermisosCatalogo();
    const [editando, setEditando] = useState(null);

    if (roles.isPending) return <Spinner />;
    if (roles.error) return <ErrorState mensaje={roles.error.message} onReintentar={roles.refetch} />;
    const descripciones = Object.fromEntries((catalogo.data ?? []).map((p) => [p.clave, p.descripcion]));

    return (
        <>
            <Titulo
                descripcion="Cada rol reúne permisos. Los de sistema no se borran; Administración incluye todo."
                accion={<BotonMas etiqueta="Nuevo rol" ayuda="Crear un rol con los permisos que elijas" onClick={() => setEditando({ rol: null })} />}
            >
                Roles
            </Titulo>
            <ul className="flex flex-col gap-2">
                {roles.data.map((r) => <FilaRol key={r.id} rol={r} descripciones={descripciones} onEditar={() => setEditando({ rol: r })} />)}
            </ul>
            <Modal abierto={Boolean(editando)} titulo={editando?.rol ? `Editar ${editando.rol.nombre}` : 'Nuevo rol'} onCerrar={() => setEditando(null)} ancho="max-w-lg">
                {editando && <EditorRol key={editando.rol?.id ?? 'nuevo'} rol={editando.rol} onListo={() => setEditando(null)} />}
            </Modal>
        </>
    );
};
