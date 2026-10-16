import { useState } from 'react';
import { Copy, Edit, Trash } from 'tesela/react';
import { Button } from '@/components/Button';
import { BarraEdicion } from '@/components/edicion/Editable';
import { BotonIcono, ControlesOrden } from '@/components/editor/ListaOrdenable';
import { useGuardarSeccion, useSeccionEditor } from '@/hooks/useEditor';
import { mover } from '@/utils/editor';

export const AccionesCaso = ({ seccionId, caso, onPedir }) => {
    const detalle = useSeccionEditor(seccionId);
    const guardar = useGuardarSeccion();
    const [confirmando, setConfirmando] = useState(false);
    const bloqueado = detalle.data?.casos_bloqueados.includes(caso.id) ?? true;
    const casos = detalle.data?.datos.casos ?? [];
    const indice = casos.findIndex((c) => c.id === caso.id);
    const cambiar = (nuevos) => guardar.mutate({ id: seccionId, datos: { ...detalle.data.datos, casos: nuevos } });

    return (
        <BarraEdicion etiqueta={`Acciones de ${caso.id}`}>
            {indice >= 0 && (
                <ControlesOrden indice={indice} total={casos.length} nombre={caso.id} onMover={(delta) => cambiar(mover(casos, indice, delta))} />
            )}
            <BotonIcono etiqueta={`Editar ${caso.id}`} onClick={() => onPedir({ tipo: 'editar', casoId: caso.id })}><Edit size={16} /></BotonIcono>
            <BotonIcono etiqueta={`Duplicar ${caso.id}`} onClick={() => onPedir({ tipo: 'duplicar', casoId: caso.id })}><Copy size={16} /></BotonIcono>
            {!confirmando && (
                <BotonIcono
                    etiqueta={bloqueado && detalle.data ? `${caso.id} tiene resultados guardados: no se puede borrar` : `Borrar ${caso.id}`}
                    peligro
                    disabled={bloqueado}
                    onClick={() => setConfirmando(true)}
                >
                    <Trash size={16} />
                </BotonIcono>
            )}
            {confirmando && (
                <>
                    <Button label="Confirmar borrado" small variant="danger" loading={guardar.isPending} onClick={() => cambiar(casos.filter((c) => c.id !== caso.id))} />
                    <Button label="Cancelar" small variant="link" onClick={() => setConfirmando(false)} />
                </>
            )}
            {guardar.error && <p role="alert" className="basis-full px-2 tipo-media text-xs text-error-fuerte">{guardar.error.detalle?.[0]?.msg ?? guardar.error.message}</p>}
        </BarraEdicion>
    );
};
