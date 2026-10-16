import { useState } from 'react';
import { Button } from '@/components/Button';
import { TextField } from '@/components/Field';
import { NombreProyecto } from '@/components/NombreProyecto';
import { useActualizarProyecto, useCrearProyecto } from '@/hooks/useAdmin';
import { claveDesde } from '@/utils/claves';
import { COLOR_HEX } from '@/utils/estilos';

const CLAVE = /^[a-z0-9][a-z0-9-]{0,59}$/;

const CampoColor = ({ valor, onCambiar }) => {
    const valido = !valor || COLOR_HEX.test(valor);
    return (
        <div className="mt-4 flex flex-col gap-2">
            <span className="tipo-media text-sm text-texto">Color del nombre</span>
            <div className="flex flex-wrap items-center gap-3">
                <input type="color" aria-label="Color del nombre" value={valido && valor ? valor : '#000000'} onChange={(e) => onCambiar(e.target.value.toUpperCase())} className="h-9 w-12 shrink-0 cursor-pointer rounded-lg border border-borde bg-white p-1" />
                <input aria-label="Color del nombre en hexadecimal" placeholder="#RRGGBB" value={valor} onChange={(e) => onCambiar(e.target.value)} aria-invalid={!valido} className={`h-9 w-28 rounded-lg border bg-white px-2 tipo-media text-xs text-texto ${valido ? 'border-borde' : 'border-error'}`} />
                {valor && <Button label="Usar el de la instancia" small variant="link" onClick={() => onCambiar('')} />}
            </div>
            <p className="tipo-media text-[11px] text-texto-apagado">Sin color, el nombre usa «Nombre del proyecto» de Colores.</p>
        </div>
    );
};

export const EditorProyecto = ({ proyecto, onListo }) => {
    const crear = useCrearProyecto();
    const actualizar = useActualizarProyecto();
    const guardar = proyecto ? actualizar : crear;
    const [nombre, setNombre] = useState(proyecto?.nombre ?? '');
    const [clave, setClave] = useState(proyecto?.clave ?? '');
    const [descripcion, setDescripcion] = useState(proyecto?.descripcion ?? '');
    const [color, setColor] = useState(proyecto?.color_nombre ?? '');
    const valido = nombre.trim() && CLAVE.test(clave) && (!color || COLOR_HEX.test(color));

    const enviar = (e) => {
        e.preventDefault();
        const datos = { nombre: nombre.trim(), descripcion: descripcion.trim(), color_nombre: color || null };
        guardar.mutate(proyecto ? { id: proyecto.id, ...datos } : { clave, ...datos }, { onSuccess: onListo });
    };

    return (
        <form onSubmit={enviar} className="flex flex-col">
            <TextField
                id="proyecto-nombre"
                label="Nombre"
                required
                value={nombre}
                onChange={(e) => {
                    setNombre(e.target.value);
                    if (!proyecto) setClave(claveDesde(e.target.value));
                }}
            />
            <TextField
                id="proyecto-clave"
                label="Clave"
                tooltip="Va en los enlaces (?proyecto=clave). No cambia después de crearlo."
                required
                disabled={Boolean(proyecto)}
                value={clave}
                error={clave && !CLAVE.test(clave) ? 'Minúsculas, números y guiones' : null}
                onChange={(e) => setClave(e.target.value)}
            />
            <TextField id="proyecto-descripcion" label="Descripción" multiline rows={2} value={descripcion} onChange={(e) => setDescripcion(e.target.value)} />
            <CampoColor valor={color} onCambiar={setColor} />
            <div className="mt-4 rounded-2xl bg-fondo px-4 py-3">
                <NombreProyecto nombre={nombre || 'Nombre del proyecto'} color={COLOR_HEX.test(color) ? color : null} />
            </div>
            {guardar.error && <p role="alert" className="mt-3 tipo-media text-xs text-error-fuerte">{guardar.error.message}</p>}
            <div className="mt-6 flex justify-end">
                <Button label={proyecto ? 'Guardar cambios' : 'Crear proyecto'} type="submit" disabled={!valido} loading={guardar.isPending} />
            </div>
        </form>
    );
};
