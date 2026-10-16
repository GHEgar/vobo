import { Copy, Edit, Eye, History } from 'tesela/react';
import { Chip } from '@/components/Chip';
import { BotonIcono, ControlesOrden } from '@/components/editor/ListaOrdenable';
import { OcultarYBorrar } from '@/components/editor/OcultarYBorrar';
import { useRuta } from '@/hooks/useProyecto';

export const FilaSeccion = ({ seccion, indice, total, onMover, onEditar, onDuplicar, onHistorial, onBorrada }) => {
    const ruta = useRuta();

    return (
        <li className="flex flex-col gap-3 rounded-2xl bg-fondo px-4 py-3 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex min-w-0 items-start gap-3">
                <ControlesOrden indice={indice} total={total} nombre={seccion.titulo} onMover={onMover} />
                <div className="min-w-0">
                    <p className="tipo-negrita text-sm text-texto">
                        {seccion.titulo}
                        <span className="tipo-media text-[11px] text-texto-apagado"> · {seccion.id}</span>
                    </p>
                    <div className="mt-1 flex flex-wrap gap-1">
                        <Chip>{seccion.casos === 1 ? '1 caso' : `${seccion.casos} casos`}</Chip>
                        {seccion.oculta && <Chip tono="aviso">Oculta</Chip>}
                        {seccion.con_resultados && <Chip tono="marca">Con resultados</Chip>}
                    </div>
                </div>
            </div>
            <div className="flex shrink-0 flex-wrap items-center gap-1 lg:max-w-[50%] lg:justify-end">
                {!seccion.oculta && (
                    <a href={ruta(`/seccion/${encodeURIComponent(seccion.id)}`)} target="_blank" rel="noreferrer" aria-label={`Ver ${seccion.titulo} como validador`} title="Ver como validador" className="inline-flex h-[30px] w-[30px] items-center justify-center rounded-full border border-gris bg-white text-texto-tenue hover:border-primario hover:text-primario">
                        <Eye size={16} />
                    </a>
                )}
                <BotonIcono etiqueta={`Editar ${seccion.titulo}`} onClick={onEditar}><Edit size={16} /></BotonIcono>
                <BotonIcono etiqueta={`Duplicar ${seccion.titulo}`} onClick={onDuplicar}><Copy size={16} /></BotonIcono>
                <BotonIcono etiqueta={`Historial de ${seccion.titulo}`} onClick={onHistorial}><History size={16} /></BotonIcono>
                <OcultarYBorrar seccion={seccion} onBorrada={onBorrada} />
            </div>
        </li>
    );
};
