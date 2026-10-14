import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/Button';
import { Spinner } from '@/components/Spinner';
import { ErrorState } from '@/components/Estados';
import { Tarjeta } from '@/components/Tarjeta';
import { useInstancia } from '@/hooks/useInstancia';
import { useSesion } from '@/hooks/useSesion';
import { entrarLocal, fetchModo, fetchUsuariosLocales } from '@/services/validacion';

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

const Entrar = () => {
    const { data, isPending, error, refetch } = useQuery({ queryKey: ['modo'], queryFn: fetchModo });
    const { nombre } = useInstancia();

    return (
        <main className="flex min-h-dvh items-center justify-center p-4">
            <Tarjeta className="flex w-full max-w-md flex-col gap-5">
                <div>
                    {nombre && <p className="mb-1 tipo-negrita text-xs text-aviso">{nombre}</p>}
                    <h1 className="tipo-negrita text-xl text-primario">Iniciar sesión</h1>
                    <p className="mt-2 tipo-media text-sm text-texto-tenue">
                        {data?.modo === 'local' ? 'Elige un usuario de prueba para entrar.' : 'Entra con tu cuenta.'}
                    </p>
                </div>
                {isPending && <Spinner />}
                {error && <ErrorState mensaje={error.message} onReintentar={refetch} />}
                {data?.modo === 'local' && <SelectorLocal />}
                {data?.modo === 'oidc' && (
                    <Button label="Entrar con tu cuenta" fullWidth onClick={() => window.location.assign('/api/auth/login')} />
                )}
            </Tarjeta>
        </main>
    );
};

export default Entrar;
