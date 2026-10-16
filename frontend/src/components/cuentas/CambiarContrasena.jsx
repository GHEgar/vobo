import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Button } from '@/components/Button';
import { TextField } from '@/components/Field';
import { CamposContrasena } from '@/components/cuentas/CamposContrasena';
import { problemaContrasena } from '@/utils/contrasena';
import { useSesion } from '@/hooks/useSesion';
import { cambiarContrasena } from '@/services/validacion';

export const CambiarContrasena = ({ onListo }) => {
    const { refrescar } = useSesion();
    const [actual, setActual] = useState('');
    const [nueva, setNueva] = useState('');
    const [confirmacion, setConfirmacion] = useState('');
    const cambiar = useMutation({ mutationFn: cambiarContrasena, onSuccess: () => refrescar() });

    const enviar = (e) => {
        e.preventDefault();
        cambiar.mutate({ actual, nueva });
    };

    if (cambiar.isSuccess) {
        return (
            <div className="flex flex-col gap-4">
                <p role="status" className="tipo-media text-sm text-texto-tenue">Tu contraseña cambió. Las demás sesiones con correo y contraseña se cerraron.</p>
                <div className="flex justify-end">
                    <Button label="Listo" onClick={onListo} />
                </div>
            </div>
        );
    }

    return (
        <form onSubmit={enviar} className="flex flex-col">
            <TextField id="cambiar-actual" label="Contraseña actual" type="password" autoComplete="current-password" required value={actual} onChange={(e) => setActual(e.target.value)} />
            <CamposContrasena prefijo="cambiar" nueva={nueva} confirmacion={confirmacion} onNueva={setNueva} onConfirmacion={setConfirmacion} />
            {cambiar.error && <p role="alert" className="mt-3 tipo-media text-xs text-error-fuerte">{cambiar.error.message}</p>}
            <div className="mt-6 flex justify-end">
                <Button label="Cambiar contraseña" type="submit" disabled={!actual || Boolean(problemaContrasena(nueva, confirmacion)) || nueva !== confirmacion} loading={cambiar.isPending} />
            </div>
        </form>
    );
};
