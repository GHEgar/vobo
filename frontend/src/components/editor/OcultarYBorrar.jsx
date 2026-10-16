import { useState } from 'react';
import { Eye, EyeOff, Trash } from 'tesela/react';
import { Button } from '@/components/Button';
import { BotonIcono } from '@/components/editor/ListaOrdenable';
import { useBorrarSeccion, useOcultarSeccion } from '@/hooks/useEditor';

export const OcultarYBorrar = ({ seccion, onBorrada }) => {
    const borrar = useBorrarSeccion();
    const ocultar = useOcultarSeccion();
    const [confirmando, setConfirmando] = useState(false);
    const error = borrar.error ?? ocultar.error;

    return (
        <>
            <BotonIcono
                etiqueta={seccion.oculta ? `Mostrar ${seccion.titulo}` : `Ocultar ${seccion.titulo}`}
                disabled={ocultar.isPending}
                onClick={() => ocultar.mutate({ id: seccion.id, oculta: !seccion.oculta })}
            >
                {seccion.oculta ? <Eye size={16} /> : <EyeOff size={16} />}
            </BotonIcono>
            {!confirmando && (
                <BotonIcono
                    etiqueta={seccion.con_resultados ? 'Tiene resultados guardados: ocúltala en vez de borrarla' : `Borrar ${seccion.titulo}`}
                    peligro
                    disabled={seccion.con_resultados}
                    onClick={() => setConfirmando(true)}
                >
                    <Trash size={16} />
                </BotonIcono>
            )}
            {confirmando && (
                <>
                    <Button label="Confirmar borrado" small variant="danger" loading={borrar.isPending} onClick={() => borrar.mutate(seccion.id, { onSuccess: onBorrada })} />
                    <Button label="Cancelar" small variant="link" onClick={() => setConfirmando(false)} />
                </>
            )}
            {error && <p role="alert" className="basis-full tipo-media text-xs text-error-fuerte">{error.message}</p>}
        </>
    );
};
