import { useState } from 'react';
import { Button } from '@/components/Button';
import { Checkbox } from '@/components/Checkbox';
import { TextField } from '@/components/Field';
import { useActualizarRol, useCrearRol, usePermisosCatalogo } from '@/hooks/useAdmin';
import { claveDesde } from '@/utils/claves';

const CLAVE_ADMIN = 'administracion';

export const EditorRol = ({ rol, onListo }) => {
    const catalogo = usePermisosCatalogo();
    const crear = useCrearRol();
    const actualizar = useActualizarRol();
    const guardar = rol ? actualizar : crear;
    const [nombre, setNombre] = useState(rol?.nombre ?? '');
    const [clave, setClave] = useState(rol?.clave ?? '');
    const [descripcion, setDescripcion] = useState(rol?.descripcion ?? '');
    const [permisos, setPermisos] = useState(rol?.permisos ?? []);
    const esAdmin = rol?.clave === CLAVE_ADMIN;

    const enviar = (e) => {
        e.preventDefault();
        const datos = { nombre: nombre.trim(), descripcion: descripcion.trim(), ...(esAdmin ? {} : { permisos }) };
        guardar.mutate(rol ? { id: rol.id, ...datos } : { clave, ...datos }, { onSuccess: onListo });
    };

    return (
        <form onSubmit={enviar} className="flex flex-col">
            <TextField
                id="rol-nombre"
                label="Nombre"
                required
                value={nombre}
                onChange={(e) => {
                    setNombre(e.target.value);
                    if (!rol) setClave(claveDesde(e.target.value));
                }}
            />
            <TextField
                id="rol-clave"
                label="Clave"
                tooltip="Identificador del rol para el mapeo de grupos del proveedor. No cambia después de crearlo."
                required
                disabled={Boolean(rol)}
                pattern="[a-z0-9][a-z0-9\-]{1,59}"
                value={clave}
                onChange={(e) => setClave(e.target.value)}
            />
            <TextField id="rol-descripcion" label="Descripción" multiline rows={2} value={descripcion} onChange={(e) => setDescripcion(e.target.value)} />
            <fieldset className="mt-4 flex flex-col gap-3">
                <legend className="mb-3 tipo-media text-sm text-texto">Permisos</legend>
                {esAdmin && <p className="tipo-media text-xs text-texto-apagado">Administración incluye todos los permisos y no se puede cambiar.</p>}
                {!esAdmin && (catalogo.data ?? []).map((p) => (
                    <Checkbox
                        key={p.clave}
                        id={`rol-permiso-${p.clave}`}
                        checked={permisos.includes(p.clave)}
                        onChange={(marcado) => setPermisos(marcado ? [...permisos, p.clave] : permisos.filter((c) => c !== p.clave))}
                    >
                        {p.descripcion}
                        <span className="block tipo-media text-[11px] text-texto-apagado">{p.clave}</span>
                    </Checkbox>
                ))}
            </fieldset>
            {guardar.error && <p role="alert" className="mt-3 tipo-media text-xs text-error-fuerte">{guardar.error.message}</p>}
            <div className="mt-6 flex justify-end">
                <Button label={rol ? 'Guardar cambios' : 'Crear rol'} type="submit" disabled={!nombre.trim() || clave.length < 2} loading={guardar.isPending} />
            </div>
        </form>
    );
};
