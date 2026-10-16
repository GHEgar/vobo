import { Checkbox } from '@/components/Checkbox';

export const SelectorRoles = ({ prefijo, roles, elegidos, onCambiar }) => (
    <fieldset className="flex flex-col gap-3">
        <legend className="mb-3 tipo-media text-sm text-texto">Roles</legend>
        {roles.map((rol) => (
            <Checkbox
                key={rol.clave}
                id={`${prefijo}-${rol.clave}`}
                checked={elegidos.includes(rol.clave)}
                onChange={(marcado) => onCambiar(marcado ? [...elegidos, rol.clave] : elegidos.filter((c) => c !== rol.clave))}
            >
                <span className="tipo-negrita">{rol.nombre}</span>
                {rol.descripcion && <span className="block tipo-media text-xs text-texto-apagado">{rol.descripcion}</span>}
            </Checkbox>
        ))}
    </fieldset>
);
