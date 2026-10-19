import { useState } from 'react';
import { Button } from '@/components/Button';
import { BotonMas } from '@/components/BotonMas';
import { Modal } from '@/components/Modal';
import { Spinner } from '@/components/Spinner';
import { ErrorState } from '@/components/Estados';
import { Titulo } from '@/components/Tarjeta';
import { EnlaceGenerado } from '@/components/admin/EnlaceGenerado';
import { FilaPersona } from '@/components/admin/FilaPersona';
import { InvitarPersona } from '@/components/admin/InvitarPersona';
import { RolesDePersona } from '@/components/admin/RolesDePersona';
import { useCrearRestablecimiento, useInvitaciones, usePersonas, useRevocarInvitacion, useRoles } from '@/hooks/useAdmin';
import { useModo } from '@/hooks/useModo';
import { useSesion } from '@/hooks/useSesion';
import { formatearFecha } from '@/utils/formato';
import { PERMISOS } from '@/utils/permisos';

const Invitaciones = ({ nombresDeRol }) => {
    const { data = [] } = useInvitaciones();
    const revocar = useRevocarInvitacion();
    if (!data.length) return null;
    return (
        <div className="mb-5 flex flex-col gap-2">
            <h3 className="tipo-negrita text-sm text-texto">Invitaciones pendientes</h3>
            <ul className="flex flex-col gap-2">
                {data.map((i) => (
                    <li key={i.id} className="flex flex-wrap items-center justify-between gap-2 rounded-2xl border border-borde px-4 py-2">
                        <span className="tipo-media text-xs text-texto-tenue">
                            <span className="tipo-negrita text-texto">{i.email}</span>
                            {' · '}{i.roles.map((c) => nombresDeRol[c] ?? c).join(', ') || 'sin roles'} · vence el {formatearFecha(i.expira)}
                        </span>
                        <Button label="Revocar" small variant="enlaceRojo" loading={revocar.isPending && revocar.variables === i.id} onClick={() => revocar.mutate(i.id)} />
                    </li>
                ))}
            </ul>
        </div>
    );
};

export const Personas = () => {
    const personas = usePersonas();
    const roles = useRoles();
    const restablecer = useCrearRestablecimiento();
    const { conCuentas: cuentasActivas } = useModo();
    const { usuario, puede } = useSesion();
    const conCuentas = cuentasActivas && puede(PERMISOS.gestionarPersonas);
    const asignaRoles = puede(PERMISOS.gestionarRoles);
    const [modal, setModal] = useState(null);
    const cerrar = () => {
        setModal(null);
        restablecer.reset();
    };

    if (personas.isPending || roles.isPending) return <Spinner />;
    const error = personas.error || roles.error;
    if (error) return <ErrorState mensaje={error.message} onReintentar={() => { personas.refetch(); roles.refetch(); }} />;
    const nombresDeRol = Object.fromEntries(roles.data.map((r) => [r.clave, r.nombre]));

    return (
        <>
            <Titulo
                descripcion="Quién entró a la instancia, con qué roles y cómo entra."
                accion={conCuentas && <BotonMas etiqueta="Invitar persona" ayuda="Generar un enlace para que alguien cree su cuenta" onClick={() => setModal({ tipo: 'invitar' })} />}
            >
                Personas
            </Titulo>
            {conCuentas && <Invitaciones nombresDeRol={nombresDeRol} />}
            <ul className="flex flex-col gap-2">
                {personas.data.map((p) => (
                    <FilaPersona
                        key={p.id}
                        persona={p}
                        nombresDeRol={nombresDeRol}
                        esYo={p.email === usuario.email}
                        conCuentas={conCuentas}
                        gestionaCuentas={puede(PERMISOS.gestionarPersonas)}
                        onRoles={asignaRoles ? () => setModal({ tipo: 'roles', persona: p }) : undefined}
                        onRestablecer={() => {
                            setModal({ tipo: 'restablecer', persona: p });
                            restablecer.mutate(p.id);
                        }}
                    />
                ))}
            </ul>
            <Modal abierto={modal?.tipo === 'invitar'} titulo="Invitar persona" onCerrar={cerrar} ancho="max-w-lg">
                <InvitarPersona roles={roles.data} onListo={cerrar} />
            </Modal>
            <Modal abierto={modal?.tipo === 'roles'} titulo={`Roles de ${modal?.persona?.nombre ?? ''}`} onCerrar={cerrar} ancho="max-w-lg">
                {modal?.persona && <RolesDePersona persona={modal.persona} roles={roles.data} onListo={cerrar} />}
            </Modal>
            <Modal abierto={modal?.tipo === 'restablecer'} titulo="Restablecer contraseña" onCerrar={cerrar} ancho="max-w-lg">
                {restablecer.isPending && <Spinner />}
                {restablecer.error && <p role="alert" className="tipo-media text-xs text-error-fuerte">{restablecer.error.message}</p>}
                {restablecer.data && (
                    <EnlaceGenerado
                        enlace={restablecer.data.enlace}
                        expira={restablecer.data.expira}
                        descripcion={`Comparte este enlace con ${modal?.persona?.email}. Los enlaces anteriores dejan de servir.`}
                    />
                )}
            </Modal>
        </>
    );
};
