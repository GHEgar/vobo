import { useState } from 'react';
import { Button } from '@/components/Button';
import { TextField } from '@/components/Field';
import { ListaOrdenable } from '@/components/editor/ListaOrdenable';
import { ResumenErrores } from '@/components/editor/ResumenErrores';
import { useCrearProcedimiento, useGuardarProcedimiento } from '@/hooks/useEditor';
import { claveDesde } from '@/utils/claves';
import { erroresDe, procedimientoVacio } from '@/utils/editor';

export const FormProcedimiento = ({ procedimiento, onListo }) => {
    const crear = useCrearProcedimiento();
    const guardar = useGuardarProcedimiento();
    const mutacion = procedimiento ? guardar : crear;
    const [datos, setDatos] = useState(procedimiento?.datos ?? procedimientoVacio());
    const [idManual, setIdManual] = useState(false);
    const errores = erroresDe(mutacion.error);
    const pasos = Array.isArray(datos.pasos) ? datos.pasos : [];

    const enviar = (e) => {
        e.preventDefault();
        e.stopPropagation();
        const opciones = { onSuccess: (r) => onListo(r) };
        if (procedimiento) guardar.mutate({ id: procedimiento.id, datos }, opciones);
        else crear.mutate(datos, opciones);
    };

    return (
        <form onSubmit={enviar} className="flex flex-col">
            <div className="grid gap-x-4 sm:grid-cols-2">
                <TextField
                    id="procedimiento-titulo"
                    label="Título"
                    required
                    value={datos.titulo ?? ''}
                    error={errores.get('titulo')}
                    onChange={(e) => setDatos({ ...datos, titulo: e.target.value, ...(procedimiento || idManual ? {} : { id: claveDesde(e.target.value, 120) }) })}
                />
                <TextField
                    id="procedimiento-id"
                    label="Id"
                    required
                    tooltip="Nombra el archivo de la animación. No cambia después de crearlo."
                    disabled={Boolean(procedimiento)}
                    value={datos.id}
                    error={errores.get('id')}
                    onChange={(e) => {
                        setIdManual(true);
                        setDatos({ ...datos, id: e.target.value });
                    }}
                />
            </div>
            <div className="grid gap-x-4 sm:grid-cols-2">
                <TextField id="procedimiento-url" label="Dirección de inicio" value={datos.url_inicio ?? ''} onChange={(e) => setDatos({ ...datos, url_inicio: e.target.value })} />
                <TextField id="procedimiento-cuenta" label="Cuenta" value={datos.cuenta ?? ''} onChange={(e) => setDatos({ ...datos, cuenta: e.target.value })} />
            </div>
            <TextField id="procedimiento-descripcion" label="Descripción" multiline rows={2} value={datos.descripcion ?? ''} onChange={(e) => setDatos({ ...datos, descripcion: e.target.value })} />
            <ListaOrdenable
                titulo="Pasos"
                items={pasos}
                onChange={(lista) => setDatos({ ...datos, pasos: lista })}
                nuevo={() => ''}
                etiquetaNuevo="Agregar paso"
                nombre="paso"
                vacio="Sin pasos."
                error={errores.get('pasos')}
            >
                {(texto, i, cambiar) => <TextField id={`procedimiento-paso-${i}`} label={`Paso ${i + 1}`} value={texto} onChange={(e) => cambiar(e.target.value)} />}
            </ListaOrdenable>
            <ResumenErrores error={mutacion.error} />
            <div className="mt-6 flex justify-end">
                <Button label={procedimiento ? 'Guardar procedimiento' : 'Crear procedimiento'} type="submit" loading={mutacion.isPending} disabled={!datos.id || !datos.titulo?.trim()} />
            </div>
        </form>
    );
};
