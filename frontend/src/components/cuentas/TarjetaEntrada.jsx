import { Tarjeta } from '@/components/Tarjeta';
import { Marca } from '@/components/Marca';
import { useInstancia } from '@/hooks/useInstancia';

const TITULO_POR_OMISION = 'Iniciar sesión';

export const TarjetaEntrada = ({ titulo, descripcion, conMensaje = true, children }) => {
    const { nombre, entrada } = useInstancia();
    return (
        <main className="flex min-h-dvh items-center justify-center p-4">
            <Tarjeta className="flex w-full max-w-md flex-col gap-5">
                <div className="flex flex-col items-start gap-1">
                    <Marca variante="entrada" />
                    {nombre && <p className="tipo-negrita text-xs text-nombre">{nombre}</p>}
                </div>
                <div>
                    <h1 className="tipo-negrita text-xl text-primario">{titulo ?? (entrada.titulo || TITULO_POR_OMISION)}</h1>
                    {descripcion && <p className="mt-2 tipo-media text-sm text-texto-tenue">{descripcion}</p>}
                    {conMensaje && entrada.mensaje && <p className="mt-2 whitespace-pre-line tipo-media text-sm text-texto-tenue">{entrada.mensaje}</p>}
                </div>
                {children}
            </Tarjeta>
        </main>
    );
};
