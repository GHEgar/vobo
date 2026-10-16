import { useEffect, useState } from 'react';
import { useLocation } from 'react-router';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/Button';
import { Spinner } from '@/components/Spinner';
import { ErrorState } from '@/components/Estados';
import { TarjetaEntrada } from '@/components/cuentas/TarjetaEntrada';
import { FormularioEntrada } from '@/components/cuentas/FormularioEntrada';
import { useSesion } from '@/hooks/useSesion';
import { entrarLocal, fetchModo, fetchUsuariosLocales } from '@/services/validacion';
import { estadoEntrada, irAlLogin } from '@/utils/entrada';

const SelectorLocal = () => {
    const { refrescar } = useSesion();
    const { data: usuarios, isPending, error } = useQuery({ queryKey: ['usuarios-locales'], queryFn: fetchUsuariosLocales });
    if (isPending) return <Spinner />;
    if (error) return <ErrorState mensaje={error.message} />;
    return (
        <ul className="flex flex-col gap-3">
            {usuarios.map((u) => (
                <li key={u.clave}>
                    <button
                        type="button"
                        onClick={async () => {
                            await entrarLocal(u.clave);
                            refrescar();
                        }}
                        className="flex w-full flex-col items-start rounded-2xl bg-fondo px-5 py-4 text-left hover:bg-primario-claro"
                    >
                        <span className="tipo-negrita text-sm text-primario">{u.nombre}</span>
                        <span className="tipo-media text-xs text-texto-tenue">{u.rol}</span>
                    </button>
                </li>
            ))}
        </ul>
    );
};

const EntradaOidc = () => {
    const ubicacion = useLocation();
    const [estado] = useState(() => estadoEntrada());

    useEffect(() => {
        if (estado === 'redirigiendo') irAlLogin(ubicacion);
    }, [estado, ubicacion]);

    if (estado === 'cerrada') {
        return (
            <TarjetaEntrada titulo="Cerraste sesión" descripcion="Tu sesión terminó en este navegador. Puedes volver a entrar cuando quieras.">
                <Button label="Entrar de nuevo" fullWidth onClick={() => irAlLogin(ubicacion)} />
            </TarjetaEntrada>
        );
    }
    if (estado === 'error') {
        return (
            <TarjetaEntrada titulo="No se pudo iniciar sesión" descripcion="Volviste sin una sesión activa. Puede ser un problema momentáneo con el inicio de sesión o con las cookies del navegador.">
                <Button label="Intentar de nuevo" fullWidth onClick={() => irAlLogin(ubicacion)} />
            </TarjetaEntrada>
        );
    }
    return (
        <TarjetaEntrada descripcion="Te llevamos al inicio de sesión.">
            <div className="flex justify-center">
                <Spinner />
            </div>
        </TarjetaEntrada>
    );
};

const EntradaCuentas = ({ conOrganizacion }) => {
    const ubicacion = useLocation();
    const [estado] = useState(() => estadoEntrada());
    return (
        <TarjetaEntrada descripcion="Entra con tu correo y tu contraseña.">
            {conOrganizacion && estado === 'error' && (
                <p role="alert" className="tipo-media text-xs text-error-fuerte">No se pudo iniciar sesión con tu organización. Intenta de nuevo o entra con tu contraseña.</p>
            )}
            <FormularioEntrada />
            {conOrganizacion && (
                <>
                    <div className="flex items-center gap-3" aria-hidden="true">
                        <span className="h-px flex-1 bg-borde" />
                        <span className="tipo-media text-xs text-texto-apagado">o</span>
                        <span className="h-px flex-1 bg-borde" />
                    </div>
                    <Button label="Entrar con tu organización" variant="outline" fullWidth onClick={() => irAlLogin(ubicacion)} />
                </>
            )}
        </TarjetaEntrada>
    );
};

const Entrar = () => {
    const { data, isPending, error, refetch } = useQuery({ queryKey: ['modo'], queryFn: fetchModo });

    if (data?.modo === 'oidc') return <EntradaOidc />;
    if (data?.modo === 'cuentas' || data?.modo === 'ambos') return <EntradaCuentas conOrganizacion={data.modo === 'ambos'} />;
    if (isPending) return <Spinner pantalla />;

    return (
        <TarjetaEntrada descripcion={data?.modo === 'local' ? 'Elige un usuario de prueba para entrar.' : undefined}>
            {error && <ErrorState mensaje={error.message} onReintentar={refetch} />}
            {data?.modo === 'local' && <SelectorLocal />}
        </TarjetaEntrada>
    );
};

export default Entrar;
