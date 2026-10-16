import { EmptyState, ErrorState } from '@/components/Estados';
import { Spinner } from '@/components/Spinner';
import { EditorCaso } from '@/components/editor/EditorCaso';
import { ResumenErrores } from '@/components/editor/ResumenErrores';
import { useGuardarSeccion, useProcedimientosEditor, useSeccionEditor } from '@/hooks/useEditor';
import { casoVacio, conPrefijo, erroresDe } from '@/utils/editor';
import { idCopia } from '@/utils/edicion';
import { Search } from 'tesela/react';

const preparar = (casos, herramientas, pedido) => {
    const posicion = casos.findIndex((c) => c.id === pedido.casoId);
    if (pedido.tipo === 'nuevo') {
        return { caso: casoVacio(herramientas[0]?.id), indice: casos.length, aplicar: (c) => [...casos, c] };
    }
    if (posicion < 0) return null;
    if (pedido.tipo === 'duplicar') {
        const original = casos[posicion];
        const copia = { ...original, id: idCopia(original.id, casos.map((c) => c.id)), titulo: `${original.titulo} (copia)` };
        return { caso: copia, indice: posicion + 1, aplicar: (c) => [...casos.slice(0, posicion + 1), c, ...casos.slice(posicion + 1)] };
    }
    return { caso: casos[posicion], indice: posicion, aplicar: (c) => casos.map((x, i) => (i === posicion ? c : x)) };
};

const FormularioCaso = ({ seccionId, pedido, onCerrar, onGuardado }) => {
    const detalle = useSeccionEditor(seccionId);
    const procedimientos = useProcedimientosEditor();
    const guardar = useGuardarSeccion();

    if (detalle.isPending || procedimientos.isPending) return <Spinner />;
    if (detalle.error) return <ErrorState mensaje={detalle.error.message} onReintentar={detalle.refetch} />;
    const { datos, casos_bloqueados: bloqueados } = detalle.data;
    const herramientas = datos.herramientas ?? [];
    const plan = preparar(datos.casos ?? [], herramientas, pedido);
    if (!plan) return <EmptyState icono={Search} titulo="El caso ya no está en la sección" />;

    return (
        <EditorCaso
            caso={plan.caso}
            herramientas={herramientas}
            procedimientos={procedimientos.data ?? []}
            errores={conPrefijo(erroresDe(guardar.error), `casos.${plan.indice}`)}
            idBloqueado={pedido.tipo === 'editar' && bloqueados.includes(plan.caso.id)}
            etiquetaListo={pedido.tipo === 'editar' ? 'Guardar caso' : 'Agregar caso'}
            guardando={guardar.isPending}
            nota={null}
            onCancelar={onCerrar}
            onListo={(caso) => guardar.mutate(
                { id: seccionId, datos: { ...datos, casos: plan.aplicar(caso) } },
                { onSuccess: () => (onGuardado ? onGuardado(caso) : onCerrar()) },
            )}
        >
            <ResumenErrores error={guardar.error} />
        </EditorCaso>
    );
};

export default FormularioCaso;
