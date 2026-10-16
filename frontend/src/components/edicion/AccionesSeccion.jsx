import { Edit } from 'tesela/react';
import { BarraEdicion } from '@/components/edicion/Editable';
import { BotonIcono, ControlesOrden } from '@/components/editor/ListaOrdenable';
import { OcultarYBorrar } from '@/components/editor/OcultarYBorrar';
import { useOrdenarSecciones } from '@/hooks/useEditor';
import { intercambiar } from '@/utils/editor';

export const AccionesSeccion = ({ seccion, lista, ids, onEditar, onUsar }) => {
    const ordenar = useOrdenarSecciones();
    if (!seccion.edicion) return null;
    const indice = lista.findIndex((s) => s.id === seccion.id);

    return (
        <BarraEdicion etiqueta={`Acciones de ${seccion.titulo}`} onClickCapture={onUsar}>
            <ControlesOrden
                indice={indice}
                total={lista.length}
                nombre={seccion.titulo}
                onMover={(delta) => ordenar.mutate(intercambiar(ids, seccion.id, lista[indice + delta].id))}
            />
            <BotonIcono etiqueta={`Editar ${seccion.titulo}`} onClick={onEditar}><Edit size={16} /></BotonIcono>
            <OcultarYBorrar seccion={seccion.edicion} />
            {ordenar.error && <p role="alert" className="basis-full px-2 tipo-media text-xs text-error-fuerte">{ordenar.error.message}</p>}
        </BarraEdicion>
    );
};
