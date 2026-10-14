import { useEffect, useState } from 'react';
import { useLocation } from 'react-router';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/Button';
import { Spinner } from '@/components/Spinner';
import { ErrorState } from '@/components/Estados';
import { Tarjeta } from '@/components/Tarjeta';
import { useInstancia } from '@/hooks/useInstancia';
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

const TarjetaEntrada = ({ titulo, descripcion, children }) => {
    const { nombre } = useInstancia();
    return (
        <main className="flex min-h-dvh items-center justify-center p-4">
            <Tarjeta className="flex w-full max-w-md flex-col gap-5">
                <div>
                    {nombre && <p className="mb-1 tipo-negrita text-xs text-aviso">{nombre}</p>}
                    <h1 className="tipo-negrita text-xl text-primario">{titulo}</h1>
                    {descripcion && <p className="mt-2 tipo-media text-sm text-texto-tenue">{descripcion}</p>}
                </div>
                {children}
            </Tarjeta>
        </main>
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
    return <Spinner pantalla />;
};

const Entrar = () => {
    const { data, isPending, error, refetch } = useQuery({ queryKey: ['modo'], queryFn: fetchModo });

    if (data?.modo === 'oidc') return <EntradaOidc />;
    if (isPending) return <Spinner pantalla />;

    return (
        <TarjetaEntrada titulo="Iniciar sesión" descripcion={data?.modo === 'local' ? 'Elige un usuario de prueba para entrar.' : undefined}>
            {error && <ErrorState mensaje={error.message} onReintentar={refetch} />}
            {data?.modo === 'local' && <SelectorLocal />}
        </TarjetaEntrada>
    );
};

export default Entrar;
