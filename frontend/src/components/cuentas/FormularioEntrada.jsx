import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Button } from '@/components/Button';
import { TextField } from '@/components/Field';
import { useSesion } from '@/hooks/useSesion';
import { entrarCuenta } from '@/services/validacion';

export const FormularioEntrada = () => {
    const { refrescar } = useSesion();
    const [email, setEmail] = useState('');
    const [contrasena, setContrasena] = useState('');
    const entrar = useMutation({ mutationFn: entrarCuenta, onSuccess: () => refrescar() });

    const enviar = (e) => {
        e.preventDefault();
        entrar.mutate({ email: email.trim(), contrasena });
    };

    return (
        <form onSubmit={enviar} className="flex flex-col" noValidate>
            <TextField id="entrar-email" label="Correo" type="email" autoComplete="username" required value={email} onChange={(e) => setEmail(e.target.value)} />
            <TextField id="entrar-contrasena" label="Contraseña" type="password" autoComplete="current-password" required value={contrasena} onChange={(e) => setContrasena(e.target.value)} />
            {entrar.error && <p role="alert" className="mt-3 tipo-media text-xs text-error-fuerte">{entrar.error.message}</p>}
            <Button label="Entrar" type="submit" fullWidth className="mt-6" disabled={!email.trim() || !contrasena} loading={entrar.isPending} />
        </form>
    );
};
