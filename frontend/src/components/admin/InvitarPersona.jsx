import { useState } from 'react';
import { Button } from '@/components/Button';
import { TextField } from '@/components/Field';
import { EnlaceGenerado } from '@/components/admin/EnlaceGenerado';
import { SelectorRoles } from '@/components/admin/SelectorRoles';
import { useInvitar } from '@/hooks/useAdmin';

export const InvitarPersona = ({ roles, onListo }) => {
    const invitar = useInvitar();
    const [email, setEmail] = useState('');
    const [elegidos, setElegidos] = useState(['validador']);

    if (invitar.data) {
        return (
            <div className="flex flex-col gap-4">
                <EnlaceGenerado
                    enlace={invitar.data.enlace}
                    expira={invitar.data.expira}
                    descripcion={`Comparte este enlace con ${email.trim()}. Con él define su nombre y su contraseña.`}
                />
                <div className="flex justify-end">
                    <Button label="Listo" onClick={onListo} />
                </div>
            </div>
        );
    }

    return (
        <form
            className="flex flex-col gap-4"
            onSubmit={(e) => {
                e.preventDefault();
                invitar.mutate({ email: email.trim(), roles: elegidos });
            }}
        >
            <TextField id="invitar-email" label="Correo" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
            <SelectorRoles prefijo="invitar" roles={roles} elegidos={elegidos} onCambiar={setElegidos} />
            {invitar.error && <p role="alert" className="tipo-media text-xs text-error-fuerte">{invitar.error.message}</p>}
            <div className="flex justify-end">
                <Button label="Generar enlace" type="submit" disabled={!email.trim()} loading={invitar.isPending} />
            </div>
        </form>
    );
};
