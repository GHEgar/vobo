import { useState } from 'react';
import { Button } from '@/components/Button';
import { SelectorRoles } from '@/components/admin/SelectorRoles';
import { useAsignarRoles } from '@/hooks/useAdmin';

export const RolesDePersona = ({ persona, roles, onListo }) => {
    const asignar = useAsignarRoles();
    const [elegidos, setElegidos] = useState(persona.roles);

    return (
        <div className="flex flex-col gap-4">
            <p className="tipo-media text-sm text-texto-tenue">
                Los permisos de estos roles se suman a los que la persona ya recibe de su organización.
            </p>
            <SelectorRoles prefijo={`roles-${persona.id}`} roles={roles} elegidos={elegidos} onCambiar={setElegidos} />
            {asignar.error && <p role="alert" className="tipo-media text-xs text-error-fuerte">{asignar.error.message}</p>}
            <div className="flex justify-end">
                <Button label="Guardar roles" loading={asignar.isPending} onClick={() => asignar.mutate({ id: persona.id, roles: elegidos }, { onSuccess: onListo })} />
            </div>
        </div>
    );
};
