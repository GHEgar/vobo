import { useState } from 'react';
import { useNavigate, useParams } from 'react-router';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Button } from '@/components/Button';
import { TextField } from '@/components/Field';
import { Spinner } from '@/components/Spinner';
import { CamposContrasena } from '@/components/cuentas/CamposContrasena';
import { problemaContrasena } from '@/utils/contrasena';
import { TarjetaEntrada } from '@/components/cuentas/TarjetaEntrada';
import { useSesion } from '@/hooks/useSesion';
import { aceptarInvitacion, fetchInvitacion, fetchRestablecimiento, restablecer } from '@/services/validacion';

const FLUJOS = {
    invitacion: {
        leer: fetchInvitacion,
        enviar: aceptarInvitacion,
        titulo: 'Crea tu cuenta',
        descripcion: (email) => `Te invitaron a entrar como ${email}. Escribe tu nombre y elige una contraseña.`,
        boton: 'Crear cuenta',
        conNombre: true,
    },
    restablecer: {
        leer: fetchRestablecimiento,
        enviar: restablecer,
        titulo: 'Elige una contraseña nueva',
        descripcion: (email) => `Cuenta: ${email}. Al guardarla se cierran tus otras sesiones con contraseña.`,
        boton: 'Guardar contraseña',
        conNombre: false,
    },
};

const Formulario = ({ flujo, token, email }) => {
    const { refrescar } = useSesion();
    const navigate = useNavigate();
    const [nombre, setNombre] = useState('');
    const [nueva, setNueva] = useState('');
    const [confirmacion, setConfirmacion] = useState('');
    const enviar = useMutation({
        mutationFn: flujo.enviar,
        onSuccess: async () => {
            await refrescar();
            navigate('/', { replace: true });
        },
    });
    const incompleto = (flujo.conNombre && !nombre.trim()) || Boolean(problemaContrasena(nueva, confirmacion)) || nueva !== confirmacion;

    const alEnviar = (e) => {
        e.preventDefault();
        enviar.mutate({ token, contrasena: nueva, ...(flujo.conNombre ? { nombre: nombre.trim() } : {}) });
    };

    return (
        <TarjetaEntrada titulo={flujo.titulo} descripcion={flujo.descripcion(email)} conMensaje={false}>
            <form onSubmit={alEnviar} className="flex flex-col">
                <input type="email" autoComplete="username" value={email} readOnly hidden />
                {flujo.conNombre && <TextField id="definir-nombre" label="Tu nombre" autoComplete="name" required value={nombre} onChange={(e) => setNombre(e.target.value)} />}
                <CamposContrasena prefijo="definir" nueva={nueva} confirmacion={confirmacion} onNueva={setNueva} onConfirmacion={setConfirmacion} />
                {enviar.error && <p role="alert" className="mt-3 tipo-media text-xs text-error-fuerte">{enviar.error.message}</p>}
                <Button label={flujo.boton} type="submit" fullWidth className="mt-6" disabled={incompleto} loading={enviar.isPending} />
            </form>
        </TarjetaEntrada>
    );
};

export const DefinirContrasena = ({ tipo }) => {
    const flujo = FLUJOS[tipo];
    const { token } = useParams();
    const { data, isPending, error } = useQuery({ queryKey: [tipo, token], queryFn: () => flujo.leer(token), retry: false });

    if (isPending) return <Spinner pantalla />;
    if (error) {
        return (
            <TarjetaEntrada titulo="Este enlace ya no sirve" descripcion={error.estado === 404 ? 'El enlace no es válido, ya se usó o expiró. Pide uno nuevo a quien administra la instancia.' : error.message} conMensaje={false}>
                <Button label="Ir al inicio" fullWidth onClick={() => window.location.assign('/')} />
            </TarjetaEntrada>
        );
    }
    return <Formulario flujo={flujo} token={token} email={data.email} />;
};
